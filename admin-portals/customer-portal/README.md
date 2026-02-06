# Seleen Customer Portal

Self-service admin portal for Seleen customers to manage licenses, users, and billing.

## Features

- 🔐 Authentication with FastAPI backend
- 📊 Dashboard with organization overview
- 👥 User management (activate/deactivate seats)
- 💳 Billing management with Stripe integration
- 📈 Usage analytics and reporting
- 🔄 Admin ownership transfer
- ⚙️ Organization settings

## Tech Stack

- **Framework**: Next.js 14 (App Router)
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

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build for Production

```bash
npm run build
npm run start
```

## Project Structure

```
customer-portal/
├── app/
│   ├── login/          # Authentication pages
│   ├── dashboard/      # Main dashboard
│   ├── users/          # User management
│   ├── billing/        # Billing & invoices
│   ├── analytics/      # Usage analytics
│   ├── settings/       # Organization settings
│   ├── globals.css     # Global styles with custom fonts
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Landing page
├── components/         # Reusable React components
├── lib/                # Utilities and API client
├── public/
│   ├── fonts/          # Custom fonts
│   └── logo.png        # Seleen logo
└── package.json
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://ilanapm.onrender.com/api/v1
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
```

## Deployment

Deploy to Vercel:

```bash
vercel
```

Configure custom domain: `app.seleen.com`

## API Integration

The portal connects to the FastAPI backend at `ilanapm.onrender.com/api/v1/portal/*`:

- `/portal/customer/dashboard` - Get organization overview
- `/portal/customer/users` - List and manage users
- `/portal/customer/admin-transfer` - Transfer admin ownership
- `/portal/customer/analytics` - Usage statistics

## Custom Fonts

Fonts are loaded from `/public/fonts/`:
- `helvetica-light-587ebe5a59211.ttf` - For headers
- `HFMonorita-Light.ttf` - For body text

Configured in `app/globals.css` and `tailwind.config.ts`.

## License

© 2026 Ilana Immersive LLC. All rights reserved.
