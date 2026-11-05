import { defineHastPlugin } from 'satteri';

const MAX_NAME = 60;

const firstDescendant = (node, tagName) => {
  for (const child of node.children ?? []) {
    if (child.type !== 'element') continue;
    if (child.tagName === tagName) return child;
    const found = firstDescendant(child, tagName);
    if (found) return found;
  }
  return null;
};

const shorten = (text) => {
  const clean = text.replace(/\s+/g, ' ').trim();
  return clean.length > MAX_NAME ? `${clean.slice(0, MAX_NAME - 3)}...` : clean;
};

const element = (tagName, properties, children = []) => ({ type: 'element', tagName, properties, children });
const text = (value) => ({ type: 'text', value });

export const tableRegionPlugin = () => {
  const used = new Map();
  return defineHastPlugin({
    name: 'table-region',
    element: [
      {
        filter: ['th'],
        visit(node, ctx) {
          if (ctx.textContent(node).trim() === '') ctx.appendChild(node, element('span', { className: ['sr-only'] }, [text('Item')]));
        },
      },
      {
        filter: ['table'],
        visit(node, ctx) {
          const labelSource = firstDescendant(node, 'caption') ?? firstDescendant(node, 'th');
          const name = labelSource ? shorten(ctx.textContent(labelSource)) : '';
          const base = name || 'untitled';
          const seen = (used.get(base) ?? 0) + 1;
          used.set(base, seen);
          const label = seen === 1 ? `Table: ${base}` : `Table: ${base} (${seen})`;
          ctx.insertAfter(
            node,
            element('p', { className: ['table-cue'], hidden: true, ariaHidden: 'true' }, [text('Swipe sideways to see more columns')]),
          );
          ctx.wrapNode(node, element('div', { className: ['table-scroll'], tabIndex: 0, role: 'region', ariaLabel: label }));
        },
      },
    ],
  });
};
