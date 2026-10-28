'use client';

import dynamic from 'next/dynamic';
import { useEffect, useRef, useState } from 'react';
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUpRight, BookOpen, Braces, Check, CheckCircle2, ChevronDown, ChevronRight, CircleHelp, Code2, Flag, Gamepad2, Lightbulb, LockKeyhole, Maximize2, Play, RotateCcw, Sparkles, Terminal, VolumeX, X } from 'lucide-react';
import { solutionBody } from '../components/CodeEditor';

const CodeEditor = dynamic(() => import('../components/CodeEditor'), { ssr: false, loading: () => <div className="editor-loading">Opening your Python file…</div> });
type Status = 'loading' | 'ready' | 'running' | 'failed' | 'error' | 'won';
const hints = [
  'The game already knows when she touches blue. Look at the action inside on_blue(player).',
  'jump() makes her jump every time she lands. Which action in the reference would send her toward the flag?',
  'Replace player.jump() with player.move_left(), then select Test my fix.'
];

export default function Home() {
  const [source, setSource] = useState('');
  const [original, setOriginal] = useState('');
  const [status, setStatus] = useState<Status>('loading');
  const [message, setMessage] = useState('Preparing your playground. The first visit takes a little longer.');
  const [hint, setHint] = useState(-1);
  const [tab, setTab] = useState<'mission' | 'reference'>('mission');
  const [completed, setCompleted] = useState(false);
  const [nextOpen, setNextOpen] = useState(false);
  const [runtimeKey, setRuntimeKey] = useState(0);
  const [mode, setMode] = useState<'play' | 'test'>('play');
  const [focused, setFocused] = useState(false);
  const [runtimeReady, setRuntimeReady] = useState(false);
  const [revealToken, setRevealToken] = useState(0);
  const iframe = useRef<HTMLIFrameElement>(null);
  const scene = useRef<HTMLDivElement>(null);
  const timeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetch('/lesson.py').then((response) => {
      if (!response.ok) throw new Error('The lesson source could not be loaded.');
      return response.text();
    }).then((text) => {
      setSource(text); setOriginal(text);
      const saved = localStorage.getItem('codequest-level-1-body');
      if (saved !== null) {
        const start = text.indexOf('    # EDIT START: fix the action below\n') + '    # EDIT START: fix the action below\n'.length;
        const end = text.indexOf('    # EDIT END', start);
        if (saved.endsWith('\n') && saved.length <= 2000) setSource(text.slice(0, start) + saved + text.slice(end));
      }
      setCompleted(localStorage.getItem('codequest-level-1-complete') === 'yes');
    }).catch((error) => { setStatus('error'); setMessage(error.message); });
  }, []);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      if (event.source !== iframe.current?.contentWindow || event.data?.channel !== 'codequest') return;
      const data = event.data;
      if (data.type === 'ready') {
        setRuntimeReady(true); setStatus('ready');
        setMessage('The bug is live! Click the game and use the arrow keys to explore.');
      }
      if (data.type === 'started') {
        setStatus(data.mode === 'test' ? 'running' : 'ready');
        setMessage(data.mode === 'test' ? 'Testing your code… Can she reach the flag without jumping?' : 'Your turn! Move with ← → or A / D. Jump with Space.');
      }
      if (['won', 'failed', 'error'].includes(data.type) && timeout.current) clearTimeout(timeout.current);
      if (data.type === 'won') {
        setStatus('won'); setCompleted(true); setMessage(`You fixed it! She reached the flag in ${data.seconds}s without jumping. Level 2 is unlocked.`);
        localStorage.setItem('codequest-level-1-complete', 'yes');
      }
      if (data.type === 'failed') { setStatus('failed'); setMessage(data.message + ' Change the highlighted action and try again.'); }
      if (data.type === 'error') { setStatus('error'); setMessage(data.message); }
      if (data.type === 'explored') setMessage('You reached the flag! Now use Test my fix to let your code solve the level on its own.');
    }
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!runtimeReady) setMessage('The Python engine is still downloading. Check your connection, or use Reload game to retry.');
    }, 45000);
    return () => clearTimeout(timer);
  }, [runtimeReady, runtimeKey]);
  useEffect(() => () => { if (timeout.current) clearTimeout(timeout.current); }, []);

  function run(runMode: 'play' | 'test') {
    if (!runtimeReady || !source) return;
    if (timeout.current) clearTimeout(timeout.current);
    setMode(runMode); setStatus(runMode === 'test' ? 'running' : 'ready');
    iframe.current?.contentWindow?.postMessage({ channel: 'codequest', type: 'run', mode: runMode, body: solutionBody(source) }, '*');
    if (runMode === 'play') { iframe.current?.focus(); setFocused(true); }
    if (runMode === 'test') timeout.current = setTimeout(() => {
      setStatus('error'); setMessage('The test did not finish. Reload the game and try again.');
    }, 15000);
  }
  function changeSource(value: string) {
    setSource(value); localStorage.setItem('codequest-level-1-body', solutionBody(value));
  }
  function reset() {
    setRevealToken((value) => value + 1);
    setSource(original); setHint(-1); localStorage.removeItem('codequest-level-1-body');
    if (runtimeReady) {
      setMode('play');
      iframe.current?.contentWindow?.postMessage({channel:'codequest',type:'run',mode:'play',body:solutionBody(original)}, '*');
    }
  }
  function reload() {
    if (timeout.current) clearTimeout(timeout.current);
    setRuntimeReady(false); setStatus('loading'); setRuntimeKey((key) => key + 1);
    setMessage('Restarting the Python engine…');
  }
  function key(key: string, down: boolean) { iframe.current?.contentWindow?.postMessage({channel:'codequest',type:'key',key,down}, '*'); }

  return <div className="app-shell">
    <header className="site-header">
      <a className="brand" href="/" aria-label="CodeQuest home"><span className="brand-icon"><Braces size={22} strokeWidth={2.4}/></span>code<span>quest</span><span className="beta">PLAY & LEARN</span></a>
      <div className="course-nav"><span className="course-dot"/> Python adventures <ChevronDown size={14}/></div>
      <div className="profile"><span className="xp"><Sparkles size={15}/> {completed ? '100' : '0'} XP</span><span className="avatar">Y</span></div>
    </header>

    <main>
      <div className="breadcrumbs"><span>Python adventures</span><ChevronRight size={13}/><span>Chapter 01</span><ChevronRight size={13}/><strong>The Jumping Girl</strong></div>
      <div className="title-row"><div><div className="eyebrow">A LITTLE BUG. A BIG ADVENTURE.</div><h1>The Jumping Girl<span className="level-tag">LEVEL 01</span></h1><p>Something’s not quite right. A small change can make a big difference.</p></div><div className="lesson-meta"><span><span className="tiny-bars">▂▅▇</span> Beginner</span><i/><span>~5 min</span></div></div>

      <div className="workspace">
        <aside className="mission-panel">
          <div className="panel-tabs"><button className={tab === 'mission' ? 'selected' : ''} onClick={() => setTab('mission')}><Flag size={15}/> Your mission</button><button className={tab === 'reference' ? 'selected' : ''} onClick={() => setTab('reference')}><BookOpen size={15}/> Reference</button></div>
          {tab === 'mission' ? <div className="mission-content">
            <div className="chapter-number">01 <span>/ THE FIRST ADVENTURE</span></div>
            <h2>A jump in the<br/>wrong direction.</h2>
            <p>Meet Maya. She’s on her way to the flag, but the blue platform has her a little confused.</p>
            <div className="story-callout"><span className="blue-square"/><p>When she touches <strong>blue</strong>, she should move <strong>left</strong>.<br/>Instead, she keeps jumping!</p></div>
            <h3>LET’S FIX THAT</h3>
            <ol className="steps"><li><span>1</span><p><strong>Play & observe</strong><br/>Try the game. What goes wrong?</p></li><li><span>2</span><p><strong>Find the bug</strong><br/>Read the code. Edit the green section.</p></li><li><span>3</span><p><strong>Test your fix</strong><br/>Help Maya walk left to the flag.</p></li></ol>
            <div className="goal-card"><Flag size={18}/><div><strong>Your goal</strong><p>Reach the flag by moving left on blue, without any automatic jumps.</p></div></div>
          </div> : <div className="mission-content reference-content"><div className="chapter-number">YOUR TOOLKIT</div><h2>A few helpful<br/>player actions.</h2><p>The game calls <code>on_blue(player)</code> whenever Maya is standing on the blue platform.</p>{[['player.jump()', 'Jump up from the ground.'],['player.move_left()', 'Start moving toward the left.'],['player.move_right()', 'Start moving toward the right.'],['player.stop()', 'Stop horizontal movement.']].map(([code, text]) => <div className="api-item" key={code}><code>{code}</code><p>{text}</p></div>)}<div className="reference-note"><LockKeyhole size={16}/><p>The game loop and collision code are protected. Only the highlighted function body can be changed.</p></div></div>}
          <div className="hint-section"><button onClick={() => setHint((value) => Math.min(value + 1, 2))}><Lightbulb size={17}/>{hint < 0 ? 'Need a little nudge?' : hint === 2 ? 'Solution revealed' : 'Show another hint'}<ChevronRight size={15}/></button>{hint >= 0 && <p role="status">{hints[hint]}</p>}</div>
        </aside>

        <section className="playground" aria-label="Game playground">
          <div className="section-toolbar"><span><span className="live-dot"/> THE PLAYGROUND</span><div><span className="sound-label"><VolumeX size={14}/> Sound off</span><button className="icon-button" aria-label="Fullscreen game" onClick={() => scene.current?.requestFullscreen()}><Maximize2 size={15}/></button></div></div>
          <div className="scene" ref={scene}>
            <iframe key={runtimeKey} ref={iframe} src="/runner/index.html" title="The Jumping Girl playable Pygame game" allow="autoplay; fullscreen" onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}/>
            {!runtimeReady && <div className="runtime-loading"><div className="loading-flower"><Braces size={28}/></div><strong>Waking up the adventure…</strong><span>Loading Python & Pygame</span><div className="loading-track"><i/></div></div>}
            {runtimeReady && <div className="scene-badge"><span className="live-dot"/>{mode === 'test' && status === 'running' ? 'TESTING YOUR FIX' : 'LEVEL 01 · GREENWOOD'}</div>}
            {status === 'won' && <div className="win-overlay"><div className="win-icon"><Check size={26}/></div><h2>A little fix. A big win.</h2><p>You got Maya moving in the right direction.</p><button onClick={() => setNextOpen(true)}>Next adventure <ArrowRight size={16}/></button><button className="replay-link" onClick={() => run('play')}>Play this level again</button></div>}
          </div>
          <div className="game-controls"><div className="keyboard-guide"><kbd>←</kbd><kbd>→</kbd><span>move</span><kbd className="space-key">space</kbd><span>jump</span></div><button className="play-yourself" disabled={!runtimeReady || status === 'running'} onClick={() => run('play')}><Gamepad2 size={16}/> Play yourself</button></div>
          <div className="touch-controls" aria-label="Touch game controls">{[['ArrowLeft','Move left'],['ArrowRight','Move right'],[' ','Jump']].map(([value,label]) => <button key={value} aria-label={label} disabled={!runtimeReady || mode === 'test'} onPointerDown={(event) => {event.currentTarget.setPointerCapture(event.pointerId);key(value,true);}} onPointerUp={() => key(value,false)} onPointerCancel={() => key(value,false)}>{value === 'ArrowLeft' ? <ArrowLeft size={19}/> : value === 'ArrowRight' ? <ArrowRight size={19}/> : 'Jump'}</button>)}</div>
          <div className="play-tip"><CircleHelp size={14}/>{mode === 'test' && status === 'running' ? 'Hands off! Your code is driving this attempt.' : focused ? 'You’re in control. Follow the flag to the left.' : 'Click the game to use your keyboard, or choose Play yourself.'}</div>
          <div className="console-card"><div className="console-heading"><span><Terminal size={14}/> Adventure log</span><span className={'status-pill ' + status}>{status === 'loading' ? 'LOADING' : status === 'running' ? 'RUNNING' : status === 'won' ? 'SOLVED' : status === 'failed' || status === 'error' ? 'TRY AGAIN' : 'READY'}</span></div><div className={'console-message ' + status} aria-live="polite">{status === 'won' ? <CheckCircle2 size={17}/> : <ChevronRight size={17}/>}<p>{message}</p></div></div>
          <div className="learning-note"><span>✦</span><p>Every great programmer starts with a bug.</p><span>✦</span></div>
        </section>

        <section className="editor-panel" aria-label="Python code editor"><div className="editor-titlebar"><div><Code2 size={16}/><span>main.py</span><span className="file-dot"/></div><span>PYTHON</span></div><div className="editor-notice"><LockKeyhole size={12}/><span>Full code visible. <strong>Green section editable.</strong></span><button title="Jump to editable section" aria-label="Jump to editable section" onClick={() => setRevealToken((value) => value + 1)}><ArrowDown size={13}/></button></div><div className="editor-body">{source && <CodeEditor source={source} onChange={changeSource} revealToken={revealToken}/>}</div><div className="editor-footer"><div className="editor-footer-note"><span className="edit-indicator"/> Your changes stay in this browser</div><div className="editor-actions"><button className="reset-button" onClick={reset} disabled={!original || status === 'running'} aria-label="Reset starter code"><RotateCcw size={15}/> Reset</button><button className="run-button" onClick={() => run('test')} disabled={!runtimeReady || status === 'running' || !source}><Play size={14} fill="currentColor"/>{status === 'running' ? 'Testing…' : 'Test my fix'}<span>↵</span></button></div></div></section>
      </div>

      <div className="journey"><div className="journey-title"><span className="journey-icon"><Flag size={17}/></span><div><strong>Your adventure</strong><span>One small fix at a time</span></div></div><div className="journey-stops"><div className={'journey-stop active ' + (completed ? 'done' : '')}><span>{completed ? <Check size={15}/> : '01'}</span><div><strong>The Jumping Girl</strong><small>{completed ? 'Completed · +100 XP' : 'You are here'}</small></div></div><div className="journey-line"/><button className={'journey-stop next ' + (completed ? 'unlocked' : '')} disabled={!completed} onClick={() => setNextOpen(true)}><span>{completed ? '02' : <LockKeyhole size={13}/>}</span><div><strong>The next adventure</strong><small>{completed ? 'Unlocked' : 'Complete level 1 to unlock'}</small></div></button></div><span className="journey-progress">{completed ? '1' : '0'} / 1 complete</span></div>
      <footer className="page-footer"><span>Made for curious minds.</span><button onClick={reload}><RotateCcw size={12}/> Reload game</button><span>Learn by playing. Grow by debugging.</span></footer>
    </main>
    {nextOpen && <div className="modal-backdrop" onClick={() => setNextOpen(false)}><div className="next-modal" role="dialog" aria-modal="true" aria-labelledby="next-title" onClick={(event) => event.stopPropagation()}><button className="modal-close" aria-label="Close" onClick={() => setNextOpen(false)}><X size={19}/></button><div className="modal-star"><Sparkles size={30}/></div><span className="eyebrow">LEVEL 01 COMPLETE · +100 XP</span><h2 id="next-title">Adventure unlocked.</h2><p>You spotted the wrong action and fixed it with Python. That’s debugging!</p><div className="next-preview"><span>02</span><div><strong>The next adventure</strong><p>This is a one-level demo. Your next lesson can go here.</p></div></div><button className="run-button" onClick={() => {setNextOpen(false);run('play');}}>Back to the playground <ArrowUpRight size={15}/></button></div></div>}
  </div>;
}
