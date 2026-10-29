import {AVATAR_DESIGNS,AVATAR_PALETTES,type Avatar} from '../lib/avatars';
export default function PixelAvatar({avatar,size=40}:{avatar:Avatar;size?:number}){
  const design=AVATAR_DESIGNS.find(d=>d.id===avatar.design)??AVATAR_DESIGNS[0];
  const palette=AVATAR_PALETTES.find(p=>p.id===avatar.palette)??AVATAR_PALETTES[0];
  const colors:Record<string,string>={o:palette.outline,p:palette.primary,s:palette.secondary,l:palette.light,b:palette.blue};
  return <svg role="img" aria-label={`${palette.name} ${design.name}`} viewBox="0 0 16 16" width={size} height={size} shapeRendering="crispEdges" className="pixel-avatar"><rect width="16" height="16" fill={palette.background}/>{design.pixels.flatMap((row,y)=>Array.from(row).map((pixel,x)=>colors[pixel]?<rect key={`${x},${y}`} x={x} y={y} width="1" height="1" fill={colors[pixel]}/>:null))}</svg>;
}
