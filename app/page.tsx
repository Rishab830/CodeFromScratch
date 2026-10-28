'use client';

import dynamic from 'next/dynamic';
import { useEffect, useRef, useState } from 'react';
import { ArrowDown, ArrowLeft, ArrowRight, BookOpen, Braces, Check, CheckCircle2, ChevronRight, Code2, Flag, Gamepad2, HelpCircle, Lightbulb, LockKeyhole, Maximize2, Play, RotateCcw, Sparkles, Terminal, TriangleAlert, X, Zap } from 'lucide-react';
import { solutionBody, editableRange, END } from '../components/CodeEditor';
import { LEVELS, type Level } from '../lib/levels';
import ThemeSwitch, {type Theme} from '../components/ThemeSwitch';
import LevelCoins from '../components/LevelCoins';

const CodeEditor = dynamic(() => import('../components/CodeEditor'), { ssr: false });
type Status = 'loading' | 'ready' | 'compiling' | 'playing' | 'dead' | 'error' | 'won';
const formatBytes = (bytes:number) => bytes < 1048576 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / 1048576).toFixed(1)} MB`;
const HINTS = [
  'Watch what happens when Maya lands on blue. Which action sends her toward those spikes?',
  'The game already handles your arrow keys. You can change the blue action, or remove that automatic action.',
  'Try player.move_left() instead of player.jump(). Or try pass to leave movement entirely to your controls. Compile, then play!'
];

export default function Home() {
  const [number, setNumber] = useState(1);
  const [cleared, setCleared] = useState<number[]>([]);
  const [websiteTheme,setWebsiteTheme] = useState<Theme>('dark');
  const [editorTheme,setEditorTheme] = useState<Theme>('dark');
  useEffect(() => {
    try { setCleared(LEVELS.filter((level) => localStorage.getItem(level.storage + ':complete') === 'yes').map((level) => level.number)); } catch {}
    try {
      const site = localStorage.getItem('cfs:theme:site') === 'light' ? 'light' : 'dark';
      setWebsiteTheme(site);
      setEditorTheme(localStorage.getItem('cfs:theme:editor') === 'light' ? 'light' : 'dark');
      document.documentElement.dataset.theme = site;
    } catch {}
  }, []);
  function changeWebsiteTheme(theme:Theme) {
    setWebsiteTheme(theme); document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('cfs:theme:site',theme); } catch {}
  }
  function changeEditorTheme(theme:Theme) {
    setEditorTheme(theme);
    try { localStorage.setItem('cfs:theme:editor',theme); } catch {}
  }
  const level = LEVELS.find((entry) => entry.number === number) ?? LEVELS[0];
  return <Lesson key={level.id} level={level} cleared={cleared} websiteTheme={websiteTheme} editorTheme={editorTheme} onWebsiteTheme={changeWebsiteTheme} onEditorTheme={changeEditorTheme}
    onNavigate={(target) => { if (target === 1 || cleared.includes(1)) { setNumber(target); window.scrollTo({top:0,behavior:'smooth'}); } }}
    onComplete={() => setCleared((current) => current.includes(number) ? current : [...current,number])}/>;
}

function Lesson({level: LEVEL, cleared, onNavigate, onComplete, websiteTheme, editorTheme, onWebsiteTheme, onEditorTheme}: {level: Level; cleared: number[]; onNavigate: (number: number) => void; onComplete: () => void; websiteTheme:Theme; editorTheme:Theme; onWebsiteTheme:(theme:Theme)=>void; onEditorTheme:(theme:Theme)=>void}) {
  const [source, setSource] = useState('');
  const [original, setOriginal] = useState('');
  const [compiledBody, setCompiledBody] = useState('');
  const [status, setStatus] = useState<Status>('loading');
  const [runtimeReady, setRuntimeReady] = useState(false);
  const [runtimeKey, setRuntimeKey] = useState(0);
  const [loading, setLoading] = useState<{phase:number;label:string;fraction:number|null;loaded:number;total:number}>({phase:1,label:'Connecting to Python',fraction:null,loaded:0,total:0});
  const [loadingIssue, setLoadingIssue] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [message, setMessage] = useState('Loading your little pixel world. The first visit takes a moment.');
  const [tab, setTab] = useState<'mission' | 'reference'>('mission');
  const [hint, setHint] = useState(-1);
  const [revealToken, setRevealToken] = useState(0);
  const [modal, setModal] = useState<'help' | 'next' | null>(null);
  const [focused, setFocused] = useState(false);
  const [collectedCoins, setCollectedCoins] = useState<string[]>([]);
  const iframe = useRef<HTMLIFrameElement>(null);
  const scene = useRef<HTMLDivElement>(null);
  const applied = useRef('');
  const pending = useRef('');
  const requestTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dirty = !!source && solutionBody(source) !== compiledBody;

  useEffect(() => {
    fetch(LEVEL.source).then((response) => {
      if (!response.ok) throw new Error('The Python source could not be loaded. Reload to try again.');
      return response.text();
    }).then((text) => {
      text = text.replace(/\r\n?/g, '\n');
      setOriginal(text); setSource(text);
      applied.current = solutionBody(text); setCompiledBody(applied.current);
      try {
        const saved = localStorage.getItem(LEVEL.storage + ':body');
        if (saved && saved.endsWith('\n') && saved.length <= 8000 && !saved.includes(END)) {
          const {start,end} = editableRange(text);
          setSource(text.slice(0, start) + saved + text.slice(end));
        }
      } catch { /* The game also works when browser storage is disabled. */ }
    }).catch((error) => { setStatus('error'); setMessage(error.message); });
  }, []);

  useEffect(() => {
    function receive(event: MessageEvent) {
      if (event.source !== iframe.current?.contentWindow || event.data?.channel !== 'scratch') return;
      const data = event.data;
      if (data.type === 'loading' && Number.isInteger(data.phase) && data.phase >= 1 && data.phase <= 4) {
        setLoading((current) => data.phase < current.phase ? current : {
          phase:data.phase,label:String(data.label),
          fraction:typeof data.fraction === 'number' && Number.isFinite(data.fraction) ? Math.max(0,Math.min(1,data.fraction)) : null,
          loaded:Math.max(0,Number(data.loaded) || 0),total:Math.max(0,Number(data.total) || 0)
        });
      }
      if (data.type === 'load-error') setLoadingIssue('A game download failed. Check your connection and try again.');
      if (data.type === 'ready') {
        setRuntimeReady(true); setStatus('ready');
        setMessage('Your world is ready. Play the level, spot the bug, and find your own way to the flag.');
      }
      if (data.type === 'started') {
        if (requestTimer.current) clearTimeout(requestTimer.current);
        applied.current = pending.current; setCompiledBody(pending.current);
        setAttempt(data.attempt); setStatus('playing');
        setMessage('Use the arrow keys to move and Space to jump. ' + LEVEL.log);
      }
      if (data.type === 'dead') {
        setStatus('dead'); setMessage(LEVEL.death + ' Restart to try again, or edit your code and Compile.');
      }
      if (data.type === 'won') {
        setCollectedCoins(LEVEL.coins.filter(name => Array.isArray(data.coins) && data.coins.includes(name)));
        setStatus('won');
        onComplete();
        setMessage('Flag reached! You cleared the level. Your route, your solution. +100 XP');
        try { localStorage.setItem(LEVEL.storage + ':complete', 'yes'); } catch {}
      }
      if (data.type === 'error') {
        if (requestTimer.current) clearTimeout(requestTimer.current);
        setStatus('error'); setMessage(data.message);
      }
    }
    window.addEventListener('message', receive);
    return () => { window.removeEventListener('message', receive); if (requestTimer.current) clearTimeout(requestTimer.current); };
  }, []);

  useEffect(() => {
    if (runtimeReady) return;
    const timer = setTimeout(() => {
      setMessage('The game engine is still loading. Check your connection or retry the download.');
      setLoadingIssue((current) => current || 'Taking longer than usual. The first download can be slow; you can keep waiting or retry.');
    }, 45000);
    return () => clearTimeout(timer);
  }, [runtimeReady, runtimeKey]);

  function start(body: string) {
    if (!runtimeReady) return;
    if (requestTimer.current) clearTimeout(requestTimer.current);
    pending.current = body;
    setStatus('compiling'); setMessage('Compiling Python and restarting your adventure…');
    iframe.current?.contentWindow?.postMessage({channel:'scratch',type:'compile',body}, '*');
    iframe.current?.focus();
    requestTimer.current = setTimeout(() => { setStatus('error'); setMessage('The engine did not respond. Choose Reload engine and try again.'); }, 12000);
  }
  function edit(value: string) {
    setSource(value);
    try { localStorage.setItem(LEVEL.storage + ':body', solutionBody(value)); } catch {}
  }
  function resetCode() {
    edit(original); setHint(-1); setRevealToken((value) => value + 1);
    setMessage('Starter code restored in the editor. Compile to apply it to the game.');
  }
  function reload() {
    if (requestTimer.current) clearTimeout(requestTimer.current);
    setRuntimeReady(false); setStatus('loading'); setRuntimeKey((value) => value + 1);
    setLoading({phase:1,label:'Connecting to Python',fraction:null,loaded:0,total:0}); setLoadingIssue('');
    if (original) { applied.current = solutionBody(original); setCompiledBody(applied.current); }
    setMessage('Reloading the game engine…');
  }
  function gameKey(key: string, down: boolean) {
    iframe.current?.contentWindow?.postMessage({channel:'scratch',type:'key',key,down}, '*');
  }
  function checkGamePage() {
    const document = iframe.current?.contentDocument;
    if (document && document.readyState === 'complete' && document.URL !== 'about:blank' && !document.getElementById('canvas')) {
      setLoadingIssue('The game page could not be opened. Please reload and try again.');
      setMessage('The game page is unavailable. Please reload and try again.');
    }
  }
  // A static iframe may finish before React hydrates and attaches onLoad.
  useEffect(() => { checkGamePage(); }, [runtimeKey]);
  const busy = !runtimeReady || status === 'compiling';
  const isSecond = LEVEL.number === 2;
  const loadPercent = Math.round(((loading.phase - 1 + (loading.fraction ?? 0)) / 4) * 100);
  const downloadDetail = loading.total > 0 ? `${formatBytes(loading.loaded)} / ${formatBytes(loading.total)}` : loading.loaded > 0 ? `${formatBytes(loading.loaded)} downloaded` : 'Preparing…';

  return <div className="app-shell">
    <header className="site-header">
      <a className="brand" href="/" aria-label="Code From Scratch home"><span className="brand-icon"><Braces size={23}/></span><span>code<span className="brand-middle">from</span>scratch<span className="brand-period">.</span></span></a>
      <nav aria-label="Main navigation"><a className="active" href="#levels">Adventures</a><button onClick={() => setModal('help')}>How to play <HelpCircle size={14}/></button></nav>
      <div className="profile"><ThemeSwitch scope="website" value={websiteTheme} onChange={onWebsiteTheme}/><span className="xp"><Sparkles size={15}/> {cleared.length * 100} XP</span><span className="avatar">YOU</span></div>
    </header>

    <main>
      <div className="breadcrumbs"><a href="#levels">Your adventures</a><ChevronRight size={12}/><span>World 01</span><ChevronRight size={12}/><span className="breadcrumb-current">{LEVEL.world}</span></div>
      <div className="title-row"><div><div className="eyebrow"><span/> LITTLE BUGS. BIG ADVENTURES.</div><h1>{LEVEL.title} <span className="level-tag">LVL {String(LEVEL.number).padStart(2,'0')}</span></h1><p>A curious little world. One troublesome line of code. Your move.</p></div><div className="level-reward"><span className="reward-icon"><Flag size={21}/></span><div><strong>Find your way to the flag</strong><span>Any route counts. You’ve got this.</span></div><span className="reward-xp">+100 XP</span></div></div>

      <div className="workspace">
        <section className="game-panel" aria-label="Playable level">
          <div className="lesson-card"><div className="panel-tabs"><button className={tab === 'mission' ? 'selected' : ''} onClick={() => setTab('mission')}><Flag size={15}/> The mission</button><button className={tab === 'reference' ? 'selected' : ''} onClick={() => setTab('reference')}><BookOpen size={15}/> Player actions</button><span className="beginner-tag">BEGINNER FRIENDLY</span></div>
            {tab === 'mission' ? <div className="mission-content"><div className="mission-story"><span className="story-icon"><span/></span><div><h2>{LEVEL.missionTitle}</h2><p>{LEVEL.mission}</p></div></div><div className="mission-steps"><div><span>01</span><strong>Play & notice</strong><p>Find out what goes wrong.</p></div><div><span>02</span><strong>Edit & compile</strong><p>Change the green code section.</p></div><div><span>03</span><strong>Find your way</strong><p>Play to the flag. Any solution wins.</p></div></div></div> : <div className="reference-content"><p>{isSecond ? <>This time, blue WILL make Maya jump. That part of the code is locked. Read the file and explore the game.</> : <>The game calls <code>on_blue(player)</code> when Maya stands on blue. The rest of her movement is up to you.</>}</p><div className="api-grid">{(isSecond ? [['Left / Right','Move left or right.'],['Space','Jump from solid ground.'],['Blue','Maya will jump.']] : [['player.jump()','Jump from the ground.'],['player.move_left()','Move toward the left.'],['player.move_right()','Move toward the right.'],['player.stop()','Stop sideways movement.'],['pass','Do nothing. Let the controls do the work.']]).map(([code,text]) => <div key={code}><code>{code}</code><p>{text}</p></div>)}</div></div>}
            {!isSecond && <div className="hint-section"><button onClick={() => setHint((value) => Math.min(2,value + 1))}><Lightbulb size={15}/>{hint < 0 ? 'A little hint, if you need it' : hint === 2 ? 'A couple of possible solutions' : 'Another little hint'}<ChevronRight size={14}/></button>{hint >= 0 && <p role="status">{HINTS[hint]}</p>}</div>}
          </div>
          <div className="game-heading"><span><span className="live-dot"/> {LEVEL.world.toUpperCase()} <i>/</i> {String(LEVEL.number).padStart(2,'0')}</span><div><span className="attempt">{attempt ? `ATTEMPT ${String(attempt).padStart(2,'0')}` : 'LET’S EXPLORE'}</span><button className="icon-button" aria-label="Fullscreen game" onClick={() => scene.current?.requestFullscreen().catch(() => setMessage('Fullscreen is unavailable in this browser. You can still play here.'))}><Maximize2 size={15}/></button></div></div>
          <div className="scene" ref={scene}>
            <div className="game-viewport">
            <iframe key={runtimeKey} ref={iframe} src={LEVEL.runtime} onLoad={checkGamePage} title={LEVEL.title + ' playable Pygame level'} allow="autoplay; fullscreen" onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}/>
            {!runtimeReady && <div className="runtime-loading"><div className="pixel-loader"><Braces size={27}/></div><strong>Building a little adventure...</strong><span className="loading-phase" aria-live="polite">{loading.label}</span><div className="startup-progress" role="progressbar" aria-label="Game loading progress" aria-valuemin={0} aria-valuemax={100} aria-valuenow={loadPercent} aria-valuetext={`Step ${loading.phase} of 4: ${loading.label}. ${downloadDetail}`}><div className="startup-progress-fill" style={{width:`${loadPercent}%`}}/>{loading.fraction === null && <div className="startup-progress-pulse" style={{left:`${(loading.phase - 1) * 25}%`}}/>}</div><div className="loading-numbers"><span>STEP {loading.phase} OF 4</span><span>{loading.fraction !== null ? `${Math.round(loading.fraction * 100)}% - ` : ''}{downloadDetail}</span></div><div className="loading-stages">{['Python','Level','Pygame','Play'].map((label,index) => <span key={label} className={index + 1 < loading.phase ? 'done' : index + 1 === loading.phase ? 'current' : ''}>{index + 1 < loading.phase ? 'OK' : String(index + 1).padStart(2,'0')} {label}</span>)}</div>{loadingIssue ? <div className="loading-retry"><p>{loadingIssue}</p><button onClick={reload}><RotateCcw size={12}/> Retry loading</button></div> : <p className="loading-note">First load is the slowest. Your browser caches the engine for later visits.</p>}</div>}
            {runtimeReady && status === 'ready' && <div className="start-overlay"><span className="pixel-spark">✦</span><span className="scene-eyebrow">WELCOME TO {LEVEL.world.toUpperCase()}</span><h2>Small world.<br/>Big possibilities.</h2><p>{LEVEL.intro}</p><button className="play-button" onClick={() => start(applied.current)}><Play size={15} fill="currentColor"/> Play level</button></div>}
            {status === 'dead' && <div className="outcome-overlay death-overlay" role="dialog" aria-label="Game over"><div className="outcome-symbol"><TriangleAlert size={26}/></div><span className="scene-eyebrow">A BUMP IN THE ADVENTURE</span><h2>Game over<span>!</span></h2><p>{LEVEL.death}<br/>Try again, or give your code a tiny tweak.</p><button className="play-button" onClick={() => start(applied.current)}><RotateCcw size={15}/> Restart level</button><button className="text-button" onClick={() => {setRevealToken((value) => value + 1);document.querySelector('.editor-panel')?.scrollIntoView({block:'nearest',behavior:'smooth'});}}>Take me to the code <ArrowRight size={13}/></button></div>}
            {status === 'won' && <div className="outcome-overlay win-overlay" role="dialog" aria-label="Level complete"><div className="outcome-symbol"><Flag size={26}/></div><span className="scene-eyebrow">YOUR WAY WAS THE RIGHT WAY</span><h2>Level complete<span>!</span></h2><p>You reached the flag. A little persistence<br/>goes a long way.</p><LevelCoins coins={LEVEL.coins} collected={collectedCoins}/><span className="win-xp"><Sparkles size={14}/> +100 XP earned</span><button className="play-button" onClick={() => isSecond ? setModal('next') : onNavigate(2)}>{isSecond ? 'Adventures complete' : 'Next adventure'} <ArrowRight size={15}/></button><button className="text-button" onClick={() => start(applied.current)}>Play again</button></div>}
            </div>
          </div>
          <div className="game-controls"><div className="keyboard-guide"><span><kbd>←</kbd><kbd>→</kbd> Move</span><span><kbd className="space-key">SPACE</kbd> Jump</span></div><button className="restart-button" disabled={busy} onClick={() => start(applied.current)}><RotateCcw size={14}/> Restart</button></div>
          <div className="touch-controls" aria-label="On-screen game controls">{[['ArrowLeft','Move left'],['ArrowRight','Move right'],[' ','Jump']].map(([key,label]) => <button key={key} aria-label={label} disabled={status !== 'playing'} onPointerDown={(event) => { event.currentTarget.setPointerCapture(event.pointerId); gameKey(key,true); }} onPointerUp={() => gameKey(key,false)} onPointerCancel={() => gameKey(key,false)} onLostPointerCapture={() => gameKey(key,false)}>{key === 'ArrowLeft' ? <ArrowLeft size={18}/> : key === 'ArrowRight' ? <ArrowRight size={18}/> : 'Jump ↑'}</button>)}</div>
          <div className="game-footnote"><Gamepad2 size={14}/><span>{focused && status === 'playing' ? 'You’re in control. Make your own way to the flag.' : 'Click inside the game to play with your keyboard.'}</span><span className="pixel-note">YOU ARE IN CONTROL</span></div>


        </section>

        <section className="editor-panel" data-code-theme={editorTheme} aria-label="Python code editor"><div className="editor-titlebar"><div><Code2 size={17}/><span>main.py</span><span className="python-tag">PYTHON</span></div><ThemeSwitch scope="code editor" value={editorTheme} onChange={onEditorTheme}/></div><div className="editor-notice"><LockKeyhole size={12}/><span>Read everything. <strong>Edit the green section.</strong></span><button aria-label="Jump to editable section" title="Jump to editable section" onClick={() => setRevealToken((value) => value + 1)}><ArrowDown size={14}/></button></div><div className="editor-body">{source ? <CodeEditor key={LEVEL.id} source={source} onChange={edit} revealToken={revealToken} theme={editorTheme}/> : <div className="editor-loading">Opening your Python file…</div>}</div><div className="editor-footer"><div className={'compile-state ' + (dirty ? 'dirty' : '')}><span/>{dirty ? 'Uncompiled changes' : 'All changes compiled'}<span className="saved-note">Saved on this device</span></div><div className="editor-actions"><button className="reset-button" disabled={!original || status === 'compiling'} onClick={resetCode}><RotateCcw size={14}/> Reset code</button><button className="compile-button" disabled={busy || !source} onClick={() => start(solutionBody(source))}><Zap size={15}/>{status === 'compiling' ? 'Compiling…' : 'Compile'}<span aria-hidden="true">↵</span></button></div><p className="compile-explainer">Compile applies your code and restarts the game. Then it’s your turn to play.</p></div><div className="console-card"><div className="console-heading"><span><Terminal size={13}/> Adventure log</span><span className={'status-pill '+status}>{status === 'loading' ? 'LOADING' : status === 'compiling' ? 'COMPILING' : status === 'playing' ? 'PLAYING' : status === 'won' ? 'CLEARED' : status === 'dead' ? 'GAME OVER' : status === 'error' ? 'CODE ERROR' : 'READY'}</span></div><div className={'console-message '+status} aria-live="polite">{status === 'won' ? <CheckCircle2 size={15}/> : status === 'dead' || status === 'error' ? <TriangleAlert size={15}/> : <ChevronRight size={15}/>}<p>{message}</p></div></div></section>
      </div>

      <section className="journey" id="levels" aria-label="Your adventures"><div className="journey-title"><span className="journey-icon"><Flag size={17}/></span><div><strong>Your adventure map</strong><span>One small discovery at a time.</span></div></div>{LEVELS.map((entry,index) => <div className="map-entry" key={entry.id}>{index > 0 && <div className="journey-line"/>}<button className={'journey-stop ' + (entry.number === LEVEL.number ? 'active ' : '') + (entry.number === 2 ? 'next ' : '') + (cleared.includes(entry.number) ? 'done ' : '') + (entry.number === 2 && cleared.includes(1) ? 'unlocked' : '')} disabled={entry.number === 2 && !cleared.includes(1)} onClick={() => onNavigate(entry.number)}><span>{cleared.includes(entry.number) ? <Check size={16}/> : entry.number === 2 && !cleared.includes(1) ? <LockKeyhole size={13}/> : String(entry.number).padStart(2,'0')}</span><div><strong>{entry.title}</strong><small>{cleared.includes(entry.number) ? 'Flag reached - complete' : entry.number === 2 && !cleared.includes(1) ? 'Reach the flag to unlock' : entry.world + (entry.number === LEVEL.number ? ' - you are here' : ' - ready to play')}</small></div></button></div>)}<div className="map-dots" aria-hidden="true"><i/><i/><i/></div></section>
      <footer className="page-footer"><span><span className="footer-star">✦</span> Made for curious minds, from scratch.</span><button onClick={reload}><RotateCcw size={12}/> Reload engine</button><span>There’s more than one way to win.</span></footer>
    </main>

    {modal && <div className="modal-backdrop" onClick={() => setModal(null)}><div className="info-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onClick={(event) => event.stopPropagation()}><button className="modal-close" aria-label="Close" onClick={() => setModal(null)}><X size={20}/></button><span className="modal-icon">{modal === 'help' ? <Gamepad2 size={28}/> : <Sparkles size={28}/>}</span><span className="eyebrow">CODE FROM SCRATCH</span><h2 id="modal-title">{modal === 'help' ? 'Play. Tinker. Try again.' : 'Two adventures, from scratch.'}</h2>{modal === 'help' ? <><p>Use the arrow keys or A / D to move. Press Space to jump. On a phone, use the buttons below the game.</p><p>Read the full Python file and edit the green section. <strong>Compile</strong> loads your changes and restarts the level. <strong>Restart</strong> replays your last compiled code.</p><p>Your only mission: reach the flag yourself. Any route or working solution counts.</p></> : <><p>You played your way to the flag. That’s the only rule for clearing a level here.</p><div className="next-preview"><span><Check size={18}/></span><div><strong>Both flags reached</strong><p>You can revisit either level from your adventure map.</p></div></div></>}<button className="compile-button" onClick={() => setModal(null)}>{modal === 'help' ? 'Let’s play' : 'Back to the adventure'}<ArrowRight size={15}/></button></div></div>}
  </div>;
}
