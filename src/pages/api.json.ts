import type { APIRoute } from 'astro'
import { getCollection } from 'astro:content'
import { API_EXCLUDE_SLUGS } from '../config'

export const GET: APIRoute = async () => {
  const posts = await getCollection('posts')
  const pages = await getCollection('pages')

  const entries = [...posts, ...pages]
    .filter((e) => !API_EXCLUDE_SLUGS.has(e.data.slug))
    .map((e) => ({ title: e.data.title, slug: e.data.slug }))

  return new Response(JSON.stringify(entries), {
    headers: { 'Content-Type': 'application/json' },
  })
}
