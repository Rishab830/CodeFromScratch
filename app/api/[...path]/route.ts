import {handleAccountRequest} from '../../../lib/server/accounts';
export const runtime='nodejs';
export const dynamic='force-dynamic';
export const GET=handleAccountRequest;
export const POST=handleAccountRequest;
export const PATCH=handleAccountRequest;
