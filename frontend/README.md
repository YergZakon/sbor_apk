# 🎨 АгроДанные КЗ - Frontend

Modern Next.js frontend for farm management system.

## 🛠️ Tech Stack

- **Framework:** Next.js 14 (React 18, App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:**
  - TanStack Query (server state)
  - Zustand (client state)
- **Forms:** React Hook Form + Zod
- **Charts:** Recharts
- **Maps:** React Leaflet
- **HTTP Client:** Axios

## 📦 Installation

```bash
# Install dependencies
npm install
# or
yarn install
# or
pnpm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local with your values
```

## 🚀 Running

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── globals.css         # Global styles
│   ├── (auth)/             # Auth routes
│   │   ├── login/
│   │   └── register/
│   └── (dashboard)/        # Dashboard routes
│       ├── layout.tsx
│       ├── farms/
│       ├── fields/
│       └── operations/
│
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── forms/              # Reusable forms
│   ├── tables/             # Data tables
│   ├── maps/               # Map components
│   └── charts/             # Chart components
│
├── lib/
│   ├── api/                # API client
│   │   ├── client.ts
│   │   ├── farms.ts
│   │   └── fields.ts
│   ├── hooks/              # Custom hooks
│   └── utils/              # Utilities
│
├── stores/                 # Zustand stores
│   ├── auth.ts
│   └── ui.ts
│
├── types/                  # TypeScript types
│   ├── api.ts
│   └── models.ts
│
├── public/                 # Static assets
└── styles/                 # Additional styles
```

## 🎨 UI Components

Using [shadcn/ui](https://ui.shadcn.com/) - a collection of re-usable components built with Radix UI and Tailwind CSS.

To add new components:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add table
```

## 🔌 API Integration

```typescript
// Example API call
import { api } from '@/lib/api/client'

const farms = await api.get('/api/v1/farms')
```

## 🧪 Testing

```bash
# Run tests (when implemented)
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project to [Vercel](https://vercel.com)
3. Set environment variables
4. Deploy!

### Other Platforms

```bash
# Build for production
npm run build

# Output is in .next/ folder
# Can be deployed to any Node.js hosting
```

## 📝 Development

### Adding New Page

```typescript
// app/(dashboard)/newpage/page.tsx
export default function NewPage() {
  return <div>New Page</div>
}
```

### Adding API Route

```typescript
// app/api/example/route.ts
export async function GET() {
  return Response.json({ hello: 'world' })
}
```

## 🌐 Environment Variables

See `.env.example` for all available variables.

Required:
- `NEXT_PUBLIC_API_URL` - Backend API URL

## 📞 Support

GitHub: https://github.com/YergZakon/sbor_apk
