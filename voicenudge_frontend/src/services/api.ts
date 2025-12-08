import api from '../api/client';

export const verifySecurity = (email, answer) =>
  api.post('/api/auth/verify_security', { email, answer });

export default {
  verifySecurity,
};


