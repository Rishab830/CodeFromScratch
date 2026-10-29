import type { NextConfig } from 'next';
const config: NextConfig = {
  images: { unoptimized: true }, devIndicators: false,
  async rewrites(){
    return [{source:'/runner',destination:'/runner/index.html'},...Array.from({length:12},(_,i)=>({source:`/runner-${i+2}`,destination:`/runner-${i+2}/index.html`}))];
  }
};
export default config;
