import { defineHastPlugin } from 'satteri';

export const taskListLabelsPlugin = () =>
  defineHastPlugin({
    name: 'task-list-labels',
    element: {
      filter: ['input'],
      visit(node, ctx) {
        if (node.properties?.type !== 'checkbox' || node.properties?.ariaLabel) return;
        const parent = ctx.parent(node);
        const name = ctx.textContent(parent).replace(/\s+/g, ' ').trim();
        if (name) ctx.setProperty(node, 'ariaLabel', name);
      },
    },
  });
