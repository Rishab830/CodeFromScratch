import type {Avatar} from './avatars';
export type Preferences={siteTheme:'dark'|'light';editorTheme:'dark'|'light';lastLevel?:string};
export type AccountUser={id:string;name:string;email:string;avatar:Avatar;role:'student'|'admin';createdAt:string;lastLoginAt:string;preferences:Preferences};
export type SavedLevel={levelId:string;completed:boolean;coins:string[];code?:string;codeVersion?:number;hint?:number;attempts:number;updatedAt:string;completedAt?:string};
export type LevelPatch={completed?:boolean;coins?:string[];code?:string;codeVersion?:number;hint?:number;attemptIds?:string[]};
export type SessionData={user:AccountUser|null;progress:SavedLevel[]};
