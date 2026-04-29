import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';

const SITE = 'https://blog.geographer.fr';

const EXCLUDE_SLUGS = new Set(['404', 'posts', 'internet-error']);
const CHANGE_FREQUENCIES = { resume: 'yearly' };
const PRIORITIES = { 'hexpresso-fic': 0.6 };

export default defineConfig({
  site: SITE,
  trailingSlash: 'never',
  build: { format: 'file' },
  output: 'static',
  adapter: vercel(),
  integrations: [
    sitemap({
      filter: (page) => {
        const slug = new URL(page).pathname.replace(/^\/|\.html$/g, '') || 'index';
        return !EXCLUDE_SLUGS.has(slug);
      },
      serialize(item) {
        const slug = new URL(item.url).pathname.replace(/^\/|\.html$/g, '') || 'index';
        if (CHANGE_FREQUENCIES[slug]) item.changefreq = CHANGE_FREQUENCIES[slug];
        if (PRIORITIES[slug] !== undefined) item.priority = PRIORITIES[slug];
        return item;
      },
    }),
  ],
  markdown: {
    shikiConfig: {
      theme: 'github-light',
      wrap: false,
    },
  },
});
