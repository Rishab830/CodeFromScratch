/* Observe downloads without changing the responses consumed by Pygbag/WASM. */
(() => {
  const resources = new Map();
  const labels = ['', 'Downloading Python', 'Loading level files', 'Loading Pygame', 'Starting your game'];
  let phase = 1;
  let lastUpdate = 0;
  let ready = false;
  function publish(force = false) {
    if (ready || (!force && performance.now() - lastUpdate < 100)) return;
    lastUpdate = performance.now();
    const active = [...resources.values()].filter((item) => item.phase === phase);
    const loaded = active.reduce((sum,item) => sum + item.loaded, 0);
    const total = active.reduce((sum,item) => sum + item.total, 0);
    const expected = phase === 1 ? 2 : 1;
    const complete = active.length >= expected && active.every((item) => item.done);
    const computable = active.length >= expected && active.every((item) => item.total > 0 && item.loaded <= item.total);
    const fraction = complete ? 1 : computable ? Math.min(.99, loaded / total) : null;
    parent.postMessage({channel:'scratch',type:'loading',phase,label:labels[phase],loaded,total:computable ? total : 0,fraction}, '*');
  }
  window.lessonLoadPhase = (next) => {
    if (!Number.isInteger(next) || next < phase || next > 4) return;
    phase = next;
    publish(true);
  };
  window.lessonLoadFinished = () => { ready = true; };
  function resourcePhase(url) {
    if (/\/main\.(wasm|data)(?:[?#]|$)/i.test(url)) return 1;
    if (/\.apk(?:[?#]|$)/i.test(url)) return 2;
    if (/pygame[_-]ce[^/]*\.whl(?:[?#]|$)/i.test(url)) return 3;
    return 0;
  }
  function begin(url) {
    const kind = resourcePhase(url);
    if (!kind || ready) return null;
    const record = {phase:kind,loaded:0,total:0,done:false};
    resources.set(url,record);
    if (kind > phase) phase = kind;
    publish(true);
    return record;
  }
  function failed() {
    if (!ready) parent.postMessage({channel:'scratch',type:'load-error',message:'A game download failed. Check your connection and try again.'}, '*');
  }
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async (input,init) => {
    const url = String(input instanceof Request ? input.url : input);
    const item = begin(url);
    let response;
    try { response = await nativeFetch(input,init); }
    catch (error) { if (item) failed(); throw error; }
    if (item && !response.ok) failed();
    if (item && response.ok && response.body) {
      // clone() preserves the original response, MIME type and streaming WASM.
      const copy = response.clone();
      const encoding = response.headers.get('content-encoding');
      item.total = encoding && encoding !== 'identity' ? 0 : Number(response.headers.get('content-length')) || 0;
      void (async () => {
        const reader = copy.body.getReader();
        try {
          for (;;) {
            const {done,value} = await reader.read();
            if (done) break;
            item.loaded += value.byteLength;
            // Compressed responses can have a smaller wire size than the
            // decoded stream. Do not report a misleading percentage then.
            if (item.loaded > item.total) item.total = 0;
            publish();
          }
          item.done = true;
          publish(true);
        } catch { failed(); }
        finally { reader.releaseLock(); }
      })();
    }
    return response;
  };
  const nativeOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method,url,...args) {
    const item = begin(String(url));
    if (item) {
      this.addEventListener('progress',(event) => {
        item.loaded = event.loaded;
        item.total = event.lengthComputable ? event.total : 0;
        publish();
      });
      this.addEventListener('load',() => {
        if (this.status < 200 || this.status >= 300) { failed(); return; }
        item.done = true;
        publish(true);
      });
      this.addEventListener('error',failed);
    }
    return nativeOpen.call(this,method,url,...args);
  };
  publish(true);
})();
