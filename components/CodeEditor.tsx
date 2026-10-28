'use client';

import { useEffect, useMemo, useState } from 'react';
import CodeMirror, { ExternalChange } from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { EditorState } from '@codemirror/state';
import { Decoration, EditorView, ViewPlugin, ViewUpdate } from '@codemirror/view';
import type {Theme} from './ThemeSwitch';

export const START = '    # EDIT START\n';
export const END = '    # EDIT END';
export function editableRange(source: string) {
  const start = source.indexOf(START) + START.length;
  return { start, end: source.indexOf(END, start) };
}
export function solutionBody(source: string) {
  const { start, end } = editableRange(source);
  return source.slice(start, end);
}

const protectedCode = EditorState.transactionFilter.of((transaction) => {
  if (transaction.annotation(ExternalChange)) return transaction;
  if (!transaction.docChanged) return transaction;
  const { start, end } = editableRange(transaction.startState.doc.toString());
  let allowed = true;
  transaction.changes.iterChanges((from, to) => {
    if (from < start || to > end) allowed = false;
  });
  // Keep the closing marker on its own line, outside the editable body.
  const next = transaction.newDoc.toString();
  const nextRange = editableRange(next);
  if (nextRange.end <= nextRange.start || next[nextRange.end - 1] !== '\n') allowed = false;
  return allowed ? transaction : [];
});

function highlightEditable(view: EditorView) {
  const { start, end } = editableRange(view.state.doc.toString());
  const marks = [];
  for (let position = 0; position <= view.state.doc.length;) {
    const line = view.state.doc.lineAt(position);
    const editable = line.from >= start && line.from < end;
    marks.push(Decoration.line({ class: editable ? 'editable-line' : 'protected-line' }).range(line.from));
    if (line.to === view.state.doc.length) break;
    position = line.to + 1;
  }
  return Decoration.set(marks);
}
const highlightedLines = ViewPlugin.fromClass(class {
  decorations;
  constructor(view: EditorView) { this.decorations = highlightEditable(view); }
  update(update: ViewUpdate) { if (update.docChanged) this.decorations = highlightEditable(update.view); }
}, { decorations: (plugin) => plugin.decorations });

export default function CodeEditor({ source, onChange, revealToken, theme = 'dark' }: { source: string; onChange: (value: string) => void; revealToken: number; theme?:Theme }) {
  const [view, setView] = useState<EditorView | null>(null);
  const light = theme === 'light';
  const extensions = useMemo(() => [python(), protectedCode, highlightedLines,
    EditorState.tabSize.of(4), EditorView.theme({
      '&': { backgroundColor: light ? '#fffdf9' : '#1b1c27', color: light ? '#373a34' : '#ddd2e8', fontSize: '12px', height: '100%' },
      '.cm-scroller': { fontFamily: '"Cascadia Code", "Consolas", monospace', lineHeight: '1.9', overflow: 'auto' },
      '.cm-content': { padding: '18px 0 100px', caretColor: light ? '#a55c34' : '#d5b5f5' },
      '.cm-gutters': { backgroundColor: light ? '#faf8f3' : '#1b1c27', color: light ? '#8a8c7f' : '#746780', border: 'none', paddingRight: '12px' },
      '.cm-line': { paddingLeft: '12px' },
      '.cm-activeLine': { backgroundColor: 'transparent' },
      '.cm-activeLineGutter': { backgroundColor: 'transparent' },
      '.cm-selectionBackground, &.cm-focused .cm-selectionBackground': { backgroundColor: light ? '#b5d1f1 !important' : '#3b6eac !important' },
      '.cm-cursor': { borderLeftColor: light ? '#a55c34' : '#dcc2f8' },
      // CodeMirror draws selections behind the text. Keep this line tint
      // translucent so it cannot cover the selection layer underneath.
      '.editable-line': { backgroundColor: light ? 'rgba(100, 184, 105, 0.14)' : 'rgba(100, 184, 105, 0.2)', boxShadow: light ? 'inset 3px 0 #83a97d' : 'inset 3px 0 #b3d9bb' },
      '.protected-line': { opacity: light ? '.85' : '.75' },
      '.cm-matchingBracket': { backgroundColor: light ? '#dcebd7 !important' : '#57634c !important' }
    })], [light]);
  useEffect(() => {
    if (!view) return;
    const frame = requestAnimationFrame(() => {
      const { start } = editableRange(view.state.doc.toString());
      view.dispatch({ effects: EditorView.scrollIntoView(start, { y: 'center' }), selection: { anchor: start } });
    });
    return () => cancelAnimationFrame(frame);
  }, [view, revealToken]);

  return <CodeMirror value={source} height="100%" theme={theme} extensions={extensions}
    onChange={onChange} aria-label="Python source code; only the green section is editable"
    onCreateEditor={setView} basicSetup={{ foldGutter: true, highlightActiveLine: false, highlightActiveLineGutter: false, autocompletion: false, searchKeymap: true }} />;
}
