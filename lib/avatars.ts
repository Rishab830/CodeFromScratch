export const AVATAR_DESIGNS = [
  {id:'robot',name:'Bit Bot',pixels:['................','....oo....oo....','.....oooooo.....','...oooooooooo...','..oppppppppppo..','..oplpppplpppo..','..opollopollpo..','..oppppppppppo..','..opppoooopp po..'.replace(' ',''),'..oppppppppppo..','...oooooooooo...','.....osssso.....','...ooppppppoo...','..oppppppppppo..','..oooooooooooo..','................']},
  {id:'cat',name:'Pixel Cat',pixels:['................','..oo........oo..','..opoo....oopo..','..opppoooo pppo..'.replace(' ',''),'..oppppppppppo..','.oppppppppppppo.','.opplpppplppppo.','.oppoppppoppppo.','.oppppssppppppo.','..opppsspppppo..','...oppppppppo...','....oooooooo....','...oppppppppo...','..oppppppppppo..','..oooooooooooo..','................']},
  {id:'frog',name:'Froggy',pixels:['................','...oooo..oooo...','..opllpoopllpo..','..opoolppoolpo..','..oppppppppppo..','.oppppppppppppo.','.ospppppppppspo.','.oppooooooooppo.','..oppppppppppo..','...oooooooooo...','....oppppppo....','...oppppppppo...','..oppppppppppo..','.oppooppppooppo.','.oooo.oooo.oooo.','................']},
  {id:'ghost',name:'Byte Ghost',pixels:['................','.....oooooo.....','...ooppppppoo...','..oppppppppppo..','..opplpppplppo..','.oppllopplloppo.','.oppooppppooppo.','.oppppppppppppo.','.oppppssppppppo.','.ospppppppppspo.','.oppppppppppppo.','.oppppppppppppo.','.oppppppppppppo.','.oppooppoopoppo.','.ooo..oo..o.ooo.','................']},
  {id:'wizard',name:'Loop Wizard',pixels:['.......oo.......','......oppo......','.....oppppo.....','.....opslppo....','....opppppppo...','...opppppppppo..','..oooooooooooo..','....osssssso....','....osolsoso....','....osssssso....','.....ollllo.....','....opll lppo....'.replace(' ',''),'...opplllpppo...','..opppplpppppo..','..oooooooooooo..','................']},
  {id:'pilot',name:'Star Pilot',pixels:['................','.....oooooo.....','...ooppppppoo...','..oppppppppppo..','..opsssssssspo..','.opsoooooooospo.','.opsobbbbbbospo.','.opsobllllbospo.','.opsoooooooospo.','..opsssssssspo..','...oooooooooo...','....opssppo.....','...oppppppppo...','..oppsppppsppo..','..oooooooooooo..','................']},
] as const;
export const AVATAR_PALETTES = [
  {id:'lavender',name:'Lavender',primary:'#bba4ed',secondary:'#eaa8c4',light:'#f4eaff',background:'#342b4b',blue:'#9ddae3',outline:'#30273f',skin:'#ffd8bb'},
  {id:'mint',name:'Mint',primary:'#a7d9b1',secondary:'#f3ce90',light:'#efffe9',background:'#283f39',blue:'#8dcbd5',outline:'#243b37',skin:'#ffdbbc'},
  {id:'peach',name:'Peach',primary:'#f0b18d',secondary:'#c4a4e4',light:'#fff1df',background:'#50333c',blue:'#9acfd7',outline:'#49313d',skin:'#ffe0be'},
  {id:'ocean',name:'Ocean',primary:'#8bc7ec',secondary:'#a8e0d4',light:'#ecfbff',background:'#263b54',blue:'#b1b2ee',outline:'#25354b',skin:'#ffddbf'},
  {id:'candy',name:'Candy',primary:'#eda1cd',secondary:'#bba8f0',light:'#fff0f9',background:'#492c50',blue:'#9bd7ec',outline:'#432a49',skin:'#ffdfc4'},
  {id:'sunshine',name:'Sunshine',primary:'#efd17c',secondary:'#e5a4a7',light:'#fff8d8',background:'#49412b',blue:'#b7d5b3',outline:'#44352e',skin:'#ffe0c1'},
] as const;
export type Avatar = {design:string;palette:string};
export const DEFAULT_AVATAR:Avatar={design:'robot',palette:'lavender'};
export function validAvatar(value:unknown):value is Avatar {
  if(!value||typeof value!=='object')return false;
  const a=value as Avatar;
  return AVATAR_DESIGNS.some(d=>d.id===a.design)&&AVATAR_PALETTES.some(p=>p.id===a.palette);
}
