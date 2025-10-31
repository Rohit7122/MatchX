# MatchX Frontend

A high-performance cryptocurrency trading interface built with Next.js and WebSocket integration.

## Features

- Real-time cryptocurrency trading data visualization
- Live orderbook updates via WebSocket
- Trade history tracking
- Clean and responsive UI with dark mode
- Built with TypeScript for type safety

## Tech Stack

- [Next.js](https://nextjs.org/) - React framework
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS
- WebSocket - Real-time data communication
- TypeScript - Type safety

## Getting Started
1. Install dependencies:

```bash
npm install
```

2. Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
src/
├── app/              # Next.js app directory
├── components/       # Reusable React components
├── hooks/           # Custom React hooks
└── lib/             # Utility functions and helpers
```

## Configuration

The application uses several configuration variables:

```env
NEXT_PUBLIC_WS_URL=ws://localhost:8765  # WebSocket server URL
```

## Development

- CSS styling is handled through TailwindCSS
- Custom CSS variables are defined in `src/app/globals.css`
- WebSocket connection management is handled through custom hooks
