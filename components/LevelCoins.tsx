const SPRITE = [
  '..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo',
  'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..',
];

export default function LevelCoins({coins, collected}: {coins: readonly string[]; collected: readonly string[]}) {
  const count = coins.filter(name => collected.includes(name)).length;
  return <div className="level-coins" role="group" aria-label={`Coins collected: ${count} of ${coins.length}`}>
    <span>Coins collected <strong>{count} / {coins.length}</strong></span>
    {coins.map(name => {
      const filled = collected.includes(name);
      const colors: Record<string,string> = {o:filled ? '#bc843b' : '#ae9262', f:'#ffcf64', h:'#fff2b3'};
      return <svg key={name} className={'result-coin ' + (filled ? 'collected' : 'missing')} viewBox="0 0 8 10" shapeRendering="crispEdges" role="img" aria-label={`${name === 'above' ? 'Upper' : 'Lower'} coin: ${filled ? 'collected' : 'not collected'}`}>
        {SPRITE.flatMap((row,y) => [...row].map((pixel,x) => colors[pixel] && (filled || pixel === 'o') ? <rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill={colors[pixel]}/> : null))}
      </svg>;
    })}
  </div>;
}
