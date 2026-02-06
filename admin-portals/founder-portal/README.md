# Seleen Founder Portal

Super admin portal for managing the Seleen platform, customers, and system analytics.

## Features

- 🎛️ System dashboard with platform-wide metrics
- 👥 Customer management and organization details
- 📊 System analytics and ML performance monitoring
- 🔑 License generation and management
- 📈 Revenue tracking and subscription analytics
- 🔍 Customer drill-down views with activity logs

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Fonts**:
  - Headers: Helvetica Light
  - Body: HF Monorita Light
- **Backend**: FastAPI (ilanapm.onrender.com)
- **Deployment**: Vercel

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The portal will be available at [http://localhost:3001](http://localhost:3001)

### Build for Production

```bash
npm run build
npm run start
```

## Project Structure

```
founder-portal/
├── app/
│   ├── dashboard/        # System dashboard
│   ├── customers/        # Customer list and details
│   │   └── [id]/         # Individual customer page
│   ├── analytics/        # System analytics
│   ├── licenses/         # License management
│   ├── login/            # Authentication
│   ├── globals.css       # Global styles with custom fonts
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Landing page
├── public/
│   ├── fonts/            # Custom fonts
│   └── logo.png          # Seleen logo
└── package.json
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://ilanapm.onrender.com/api/v1
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-secret-here
```

## Deployment

Deploy to Vercel:

```bash
vercel
```

Configure custom domain: `admin.seleen.com`

## API Integration

The portal connects to the FastAPI backend at `ilanapm.onrender.com/api/v1/portal/*`:

- `/portal/founder/dashboard` - System-wide metrics
- `/portal/founder/customers` - List all customers
- `/portal/founder/customers/{org_id}` - Customer details
- `/portal/founder/analytics/system` - System analytics
- `/portal/founder/licenses/generate` - Generate license keys

## Pages

1. **Landing Page** (/) - Portal introduction
2. **Login** (/login) - Super admin authentication
3. **Dashboard** (/dashboard) - System overview
4. **Customers** (/customers) - All customer organizations
5. **Customer Detail** (/customers/[id]) - Individual customer view
6. **Analytics** (/analytics) - Platform analytics and ML performance
7. **Licenses** (/licenses) - License generation and management

## Access Control

This portal is restricted to super admin users only. All endpoints require:
- Valid JWT token
- `role: super_admin` in user data

## Custom Fonts

Fonts are loaded from `/public/fonts/`:
- `helvetica-light-587ebe5a59211.ttf` - For headers
- `HFMonorita-Light.ttf` - For body text

Configured in `app/globals.css` and `tailwind.config.ts`.

## License

© 2026 Ilana Immersive LLC. All rights reserved.
