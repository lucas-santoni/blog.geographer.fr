import type { APIContext } from 'astro';
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITENAME, SITE_DESCRIPTION } from '../config';

export async function GET(context: APIContext) {
  const posts = (await getCollection('posts')).sort(
    (a, b) => b.data.date.getTime() - a.data.date.getTime()
  );

  return rss({
    title: SITENAME,
    description: SITE_DESCRIPTION,
    site: context.site!,
    items: posts.map((post) => ({
      title: post.data.title.replace(/<[^>]+>/g, ''),
      pubDate: post.data.date,
      description: post.data.description,
      link: `/${post.data.slug}`,
    })),
  });
}
