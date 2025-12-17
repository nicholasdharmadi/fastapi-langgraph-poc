# Frontend Design Update

This frontend has been redesigned with a professional black and white theme using **shadcn/ui** components and **Tailwind CSS**.

## Design System

### Color Palette
- **Primary**: Black (`#000000`) - Used for primary actions and navigation
- **Background**: White (`#FFFFFF`) - Main background
- **Neutral Grays**: Various shades for borders, text, and subtle backgrounds
- **Accent Colors**: Minimal use of red for destructive actions, green for success states

### Typography
- Clean, modern sans-serif font stack (Inter, system-ui)
- Clear hierarchy with consistent sizing
- Professional weight distribution

### Components

All UI components are built with shadcn/ui and follow a consistent design language:

#### Core Components (`/src/components/ui/`)
- **Button**: Multiple variants (default, destructive, outline, secondary, ghost, link)
- **Card**: For content containers with header, content, and footer sections
- **Dialog**: Modal dialogs with overlay
- **Input**: Form inputs with consistent styling
- **Label**: Form labels
- **Textarea**: Multi-line text inputs

#### Icons
Uses **Hero Icons Solid** throughout for consistency (replaced Lucide icons per project standards).

### Layout

- **Navigation**: Horizontal navigation bar with active state indicators
- **Content**: Max-width container (7xl) with consistent padding
- **Cards**: Elevated cards with subtle shadows and borders
- **Tables**: Clean table layouts with hover states
- **Forms**: Dialog-based forms with proper spacing and validation

### Key Features

1. **Responsive Design**: Mobile-first approach with breakpoints
2. **Interactive States**: Hover, focus, and active states for all interactive elements
3. **Consistent Spacing**: Using Tailwind's spacing scale
4. **Accessibility**: Proper ARIA labels and keyboard navigation
5. **Performance**: Optimized build with tree-shaking

## Pages

### Dashboard
- Overview stats in card format
- Recent campaigns list
- Real-time updates every 5 seconds

### Campaigns
- List view with status indicators
- Create campaign modal
- Start/View actions

### Campaign Detail
- Campaign statistics
- Lead status table
- Processing logs with real-time updates

### Leads
- Data table with actions
- Create lead modal
- Delete functionality

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## New Dependencies

- `@heroicons/react`: Icon library
- `@radix-ui/react-dialog`: Accessible dialog primitive
- `@radix-ui/react-slot`: Composition utility
- `class-variance-authority`: For component variants

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES2020+ features



