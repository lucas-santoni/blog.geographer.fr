export type Project = {
  name: string;
  emoji: string;
  description: string;
};

export const PROJECTS: Project[] = [
  {
    name: 'PoC Security Pool 2019 [French]',
    emoji: '🏊‍♂️',
    description:
      'In early 2019, I teached ~30 EPITECH students the basics of computer security. This is the teaching material I wrote for this occasion. <a href="/piscine-poc-2019">Browse it here.</a>',
  },
  {
    name: 'This blog',
    emoji: '📖',
    description:
      'This blog is statically generated using <a href="https://astro.build/">Astro</a>, and hosted on <a href="https://vercel.com">Vercel</a>. Feel free to <a href="https://github.com/lucas-santoni/blog.geographer.fr">contribute</a>.',
  },
  {
    name: 'SQLi Platform',
    emoji: '💉',
    description:
      'A WEB application written in JavaScript that makes it simple to understand and visualize SQL injections. Easy to launch via Docker. <a href="https://github.com/Geospace/sqli-platform">Get it here.</a>',
  },
];
