// Mirrors examples/starter-kit/validate_plan.py. scripts/kit-rules.test.mjs runs both on the same fixtures.

export const isSet = (value) => value !== null && value !== undefined && value !== '' && value !== false && !(Array.isArray(value) && value.length === 0);

const deepEqual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

export const holds = (condition, answers) => {
  const value = answers[condition.answer];
  if ('includes' in condition) return Array.isArray(value) && value.includes(condition.includes);
  if ('equals' in condition) return deepEqual(value, condition.equals);
  if ('is_set' in condition) return isSet(value) === condition.is_set;
  throw new Error(`unknown condition: ${JSON.stringify(condition)}`);
};

export const allHold = (conditions, answers) => conditions.every((condition) => holds(condition, answers));

const outcomeHolds = (then, answers) => {
  if ('require' in then) return isSet(answers[then.require]);
  if ('forbid' in then) return !holds(then.forbid, answers);
  return holds(then, answers);
};

export const ruleQuestion = (rule) => rule.then.require ?? rule.then.forbid?.answer ?? rule.then.answer;

const codePoints = (text) => [...text].length;
const isString = (value) => typeof value === 'string';

// Python's re.fullmatch: the whole text must match. The u flag gives code-point semantics.
export const fullMatch = (pattern, text) => new RegExp(`^(?:${pattern})$`, 'u').test(text);

const checkChoice = (question, value, values) => {
  const qid = question.id;
  if (question.type === 'single') {
    if (!isString(value)) return [[`${qid}-type`, `${qid} must be one value.`]];
    return values.includes(value) ? [] : [[`${qid}-option`, `${qid} has no option '${value}'.`]];
  }
  if (!Array.isArray(value) || !value.every(isString)) return [[`${qid}-type`, `${qid} must be a list of values.`]];
  const errors = value.filter((item) => !values.includes(item)).map((item) => [`${qid}-option`, `${qid} has no option '${item}'.`]);
  if (new Set(value).size !== value.length) errors.push([`${qid}-duplicate`, `${qid} lists a value twice.`]);
  if (value.length < (question.min ?? 0)) errors.push([`${qid}-min`, `Pick at least ${question.min} for ${qid}.`]);
  if (value.length > (question.max ?? values.length)) errors.push([`${qid}-max`, `${qid} allows at most ${question.max} value(s).`]);
  return errors;
};

const checkString = (question, value) => {
  const qid = question.id;
  if (!isString(value)) return [[`${qid}-type`, `${qid} must be text.`]];
  if (codePoints(value) < (question.min ?? 0)) return [[`${qid}-min`, `${qid} is shorter than ${question.min} character(s). Leave it out instead.`]];
  if (question.max !== undefined && codePoints(value) > question.max) return [[`${qid}-max`, `${qid} is longer than ${question.max} characters.`]];
  if (question.pattern !== undefined && !fullMatch(question.pattern, value)) {
    const refused = 'no shell operator (; & | ` $ < >), quote, backslash, bracket ( ) [ ] { }, wildcard (* ?) or control character such as a tab.';
    return [[`${qid}-pattern`, `${qid} must hold a command and ${refused}`]];
  }
  return [];
};

const checkAnswer = (question, value) => {
  if (value === null || value === undefined) return [];
  if (question.type === 'boolean') return typeof value === 'boolean' ? [] : [[`${question.id}-type`, `${question.id} must be true or false.`]];
  if (question.type === 'string') return checkString(question, value);
  return checkChoice(question, value, question.options.map((option) => option.value));
};

const withDefaults = (manifest, given) =>
  Object.fromEntries(manifest.questions.map((question) => [question.id, question.id in given ? given[question.id] : (question.default ?? null)]));

const asIssue = (question) => ([id, message]) => ({ id, message, question });

/** Returns { errors, warnings, answers }. Each issue is { id, message, question }. */
export const validate = (plan, manifest) => {
  const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
  if (!isObject(plan) || !isObject(plan.answers)) {
    return { errors: [{ id: 'plan-shape', message: 'The plan must be an object with an "answers" object.', question: null }], warnings: [], answers: {} };
  }
  const known = new Set(manifest.questions.map((question) => question.id));
  const errors = Object.keys(plan.answers)
    .filter((key) => !known.has(key))
    .map((key) => ({ id: `${key}-unknown`, message: `${key} is not a question in this kit.`, question: null }));
  const answers = withDefaults(manifest, plan.answers);
  for (const question of manifest.questions) errors.push(...checkAnswer(question, answers[question.id]).map(asIssue(question.id)));
  if (errors.length) return { errors, warnings: [], answers };
  const warnings = [];
  for (const rule of manifest.rules) {
    if (allHold(rule.when, answers) && !outcomeHolds(rule.then, answers)) {
      (rule.level === 'warning' ? warnings : errors).push({ id: rule.id, message: rule.message, question: ruleQuestion(rule) });
    }
  }
  return { errors, warnings, answers };
};

/** Returns the items, the writes, the commands for the person and the skills the person chooses outside the kit. */
export const resolve = (answers, manifest) => {
  const items = manifest.items.filter((item) => allHold(item.when, answers));
  const skills = manifest.questions.find((question) => question.id === 'skills');
  const chosen = answers.skills ?? [];
  return {
    items: items.map((item) => item.id),
    writes: items.flatMap((item) => item.writes.map((write) => ({ item: item.id, ...write }))),
    run: items.flatMap((item) => item.run.map((step) => ({ item: item.id, ...step }))),
    skillsToFind: skills.options.filter((option) => chosen.includes(option.value) && !option.ships).map((option) => option.value),
  };
};

/** The options a picker shows: an option with a hosts list needs one of the chosen hosts. */
export const visibleOptions = (question, answers) =>
  (question.options ?? []).filter((option) => !option.hosts || option.hosts.some((host) => (answers.hosts ?? []).includes(host)));

/** The form shows a question unless all of its options drop out. */
export const isVisible = (question, answers) => (question.options ?? []).length === 0 || visibleOptions(question, answers).length > 0;

/** The active rules that require an answer to this question, such as a selected hook that runs the test command. */
export const requiringRules = (question, answers, manifest) =>
  manifest.rules.filter((rule) => rule.then.require === question.id && allHold(rule.when, answers));
