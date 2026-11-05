export const supportUrl = (value) => {
  if (!value) return null;
  const url = new URL(value);
  if (url.protocol !== 'https:' || url.hostname !== 'ko-fi.com' || url.port || url.username || url.password || url.pathname === '/') {
    throw new Error('Support URL must be an HTTPS Ko-fi profile URL.');
  }
  return url.href;
};
