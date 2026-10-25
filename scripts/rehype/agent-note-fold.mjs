import { defineHastPlugin } from 'satteri';

const element = (tagName, properties, children = []) => ({ type: 'element', tagName, properties, children });

export const agentNoteFoldPlugin = () =>
  defineHastPlugin({
    name: 'agent-note-fold',
    element: {
      filter: ['aside'],
      visit(node, ctx) {
        if (node.properties?.['aria-label'] !== 'Agent note') return;
        const summary = element('summary', {}, [{ type: 'text', value: 'Agent note: rules for AI software (people can skip)' }]);
        ctx.replaceNode(node, element('details', { className: ['agent-note'] }, [summary, node]));
      },
    },
  });
