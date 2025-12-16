# Gospel Keys Design System

A comprehensive design system built on **Atomic Design** principles for the Gospel Keys music education platform.

## Overview

The design system provides a cohesive, reusable, and maintainable component library that ensures consistency across the entire application.

### Design Philosophy

- **Atomic Design**: Components organized from atoms → molecules → organisms → templates
- **Mobile-First**: Responsive by default, optimized for all screen sizes
- **Accessibility**: WCAG 2.1 AA compliant components
- **Performance**: Lightweight, tree-shakable components
- **Type-Safe**: Full TypeScript support with comprehensive prop types

## Structure

```
design-system/
├── tokens/              # Design tokens (colors, typography, spacing)
│   └── index.ts
├── components/
│   ├── atoms/          # Basic building blocks
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── ProgressBar.tsx
│   │   └── ProgressCircle.tsx
│   ├── molecules/      # Composed components
│   │   ├── Card.tsx
│   │   ├── ExerciseCard.tsx
│   │   └── CurriculumCard.tsx
│   └── templates/      # Layout components
│       ├── Container.tsx
│       ├── Stack.tsx
│       └── Grid.tsx
└── README.md           # This file
```

## Installation & Usage

### Import Components

```tsx
// Import individual components
import { Button, Badge, ExerciseCard } from '@/design-system';

// Or import from specific levels
import { Button } from '@/design-system/components/atoms';
import { Card } from '@/design-system/components/molecules';
import { Container } from '@/design-system/components/templates';
```

### Using Design Tokens

```tsx
import { tokens } from '@/design-system';

// Access colors
const primaryColor = tokens.colors.primary.cyan[500];

// Access typography
const headingSize = tokens.typography.fontSize['4xl'];

// Access spacing
const padding = tokens.spacing[6];
```

## Components Reference

### Atoms (Basic Building Blocks)

#### Button
Versatile button component with multiple variants and sizes.

```tsx
<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>

<Button variant="secondary" size="lg" loading>
  Processing...
</Button>

<Button variant="ghost" icon={<PlayIcon />} iconPosition="left">
  Play Exercise
</Button>
```

**Variants:** `primary`, `secondary`, `success`, `danger`, `ghost`
**Sizes:** `sm` (32px), `md` (40px), `lg` (48px)

#### Badge
Small labels for status, categories, or counts.

```tsx
<Badge variant="success">Completed</Badge>
<Badge variant="warning" size="sm">Intermediate</Badge>
<Badge variant="primary" outlined pill>Gospel</Badge>
<Badge variant="info" dot>3 new lessons</Badge>
```

**Variants:** `default`, `primary`, `secondary`, `success`, `warning`, `error`, `info`
**Sizes:** `sm`, `md`, `lg`

#### ProgressBar
Linear progress indicator.

```tsx
<ProgressBar value={75} variant="primary" showLabel />
<ProgressBar value={50} size="lg" animated />
<ProgressBar value={30} variant="success" label="Lesson Progress" />
```

**Variants:** `default`, `primary`, `secondary`, `success`, `warning`, `error`
**Sizes:** `sm` (4px), `md` (8px), `lg` (12px)

#### ProgressCircle
Circular/radial progress indicator.

```tsx
<ProgressCircle value={85} variant="primary" size="lg" />
<ProgressCircle value={60} label="Level 5" size="md" />
<ProgressCircle value={100} variant="success" showLabel />
```

**Variants:** `primary`, `secondary`, `success`, `warning`, `error`
**Sizes:** `sm` (48px), `md` (64px), `lg` (96px), `xl` (128px)

### Molecules (Composed Components)

#### Card
Flexible container for grouping content.

```tsx
<Card variant="elevated" padding="lg" hover>
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</Card>

<Card
  variant="glass"
  header={<h3>Header</h3>}
  footer={<Button>Action</Button>}
>
  Content with header and footer
</Card>
```

**Variants:** `default`, `glass`, `bordered`, `elevated`
**Padding:** `none`, `sm`, `md`, `lg`

#### ExerciseCard
Specialized card for displaying practice exercises.

```tsx
<ExerciseCard
  title="Gospel Voicing Exercise"
  description="Practice seventh chord voicings in all keys"
  genre="gospel"
  difficulty="intermediate"
  duration={15}
  progress={60}
  bpm={120}
  onStart={handleStart}
  onContinue={handleContinue}
/>
```

**Genres:** `gospel`, `jazz`, `blues`, `neosoul`, `classical`
**Difficulty:** `beginner`, `intermediate`, `advanced`

#### CurriculumCard
Card for displaying learning paths/curricula.

```tsx
<CurriculumCard
  title="Gospel Keys Essentials"
  description="Master fundamental gospel piano techniques"
  genre="gospel"
  skillLevel="beginner"
  duration={12}
  lessonsCount={36}
  enrolled={false}
  onEnroll={handleEnroll}
/>
```

**Skill Levels:** `beginner`, `intermediate`, `advanced`, `all-levels`

### Templates (Layout Components)

#### Container
Responsive container with max-width constraints.

```tsx
<Container size="xl" padding>
  <h1>Page Content</h1>
</Container>

<Container size="full" padding={false}>
  Full-width content without padding
</Container>
```

**Sizes:** `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px), `2xl` (1536px), `full`

#### Stack
Flexbox vertical/horizontal stack with automatic spacing.

```tsx
<Stack direction="vertical" spacing={6} align="center">
  <h1>Title</h1>
  <p>Description</p>
  <Button>Action</Button>
</Stack>

<Stack direction="horizontal" spacing={4} justify="between" wrap>
  <Badge>Tag 1</Badge>
  <Badge>Tag 2</Badge>
  <Badge>Tag 3</Badge>
</Stack>
```

**Direction:** `vertical`, `horizontal`
**Spacing:** `2`, `4`, `6`, `8`, `10`, `12`, `16` (based on spacing tokens)
**Align:** `start`, `center`, `end`, `stretch`
**Justify:** `start`, `center`, `end`, `between`, `around`, `evenly`

#### Grid
Responsive grid layout with auto-fitting columns.

```tsx
<Grid cols={3} gap={6}>
  <ExerciseCard {...exercise1} />
  <ExerciseCard {...exercise2} />
  <ExerciseCard {...exercise3} />
</Grid>

<Grid cols="auto-fit" gap={4} minWidth="300px">
  {/* Auto-responsive cards */}
</Grid>
```

**Columns:** `1`, `2`, `3`, `4`, `5`, `6`, `auto-fit`, `auto-fill`
**Gap:** `2`, `4`, `6`, `8`, `10`, `12`, `16`

## Design Tokens

### Colors

#### Brand Colors
- **Primary Cyan**: `#06b6d4` - Main brand color
- **Primary Purple**: `#8b5cf6` - Secondary brand color

#### Background Colors
- **Dark**: `#0f172a` - Main dark background
- **Card**: `#1e293b` - Card/elevated surfaces
- **Hover**: `#334155` - Hover states

#### Status Colors
- **Success**: `#10b981` - Positive actions
- **Warning**: `#f59e0b` - Warnings
- **Error**: `#ef4444` - Errors/destructive actions
- **Info**: `#0ea5e9` - Informational

#### Genre Colors
- **Gospel**: `#8b5cf6` (Purple)
- **Jazz**: `#f59e0b` (Orange)
- **Blues**: `#3b82f6` (Blue)
- **Neo-Soul**: `#ec4899` (Pink)
- **Classical**: `#6366f1` (Indigo)

### Typography

#### Font Families
- **Sans**: Inter, system-ui, -apple-system, sans-serif
- **Mono**: Fira Code, Monaco, monospace

#### Font Sizes
- `6xl`: 64px (Hero headings)
- `5xl`: 48px (Page titles)
- `4xl`: 36px (Section headings)
- `3xl`: 30px (Card titles)
- `2xl`: 24px (Subsections)
- `xl`: 20px (Large body)
- `lg`: 18px (Body large)
- `base`: 16px (Body text)
- `sm`: 14px (Small text)
- `xs`: 12px (Extra small)

#### Font Weights
- **Normal**: 400
- **Medium**: 500
- **Semibold**: 600
- **Bold**: 700
- **Extrabold**: 800

### Spacing

Based on 8px grid system:
- `1`: 4px
- `2`: 8px
- `3`: 12px
- `4`: 16px
- `5`: 20px
- `6`: 24px
- `8`: 32px
- `10`: 40px
- `12`: 48px
- `16`: 64px
- `20`: 80px
- `24`: 96px
- `32`: 128px

### Border Radius
- `sm`: 4px
- `DEFAULT`: 8px
- `md`: 12px
- `lg`: 16px
- `xl`: 24px
- `2xl`: 32px
- `full`: 9999px (fully rounded)

### Shadows
- `sm`: Subtle shadow
- `DEFAULT`: Standard shadow
- `md`: Medium shadow
- `lg`: Large shadow
- `xl`: Extra large shadow
- `2xl`: Maximum shadow

### Animation

#### Durations
- `fast`: 150ms
- `base`: 200ms
- `slow`: 300ms
- `slower`: 500ms

#### Easing
- `in`: Ease in
- `out`: Ease out
- `inOut`: Ease in-out
- `bounce`: Bounce effect

## Accessibility

All components follow WCAG 2.1 AA guidelines:
- Semantic HTML elements
- ARIA attributes where needed
- Keyboard navigation support
- Focus indicators
- Color contrast ratios ≥ 4.5:1 for normal text
- Color contrast ratios ≥ 3:1 for large text

## Best Practices

### Component Composition

Build complex UIs by composing atomic components:

```tsx
// Good: Compose atoms into molecules
<Card>
  <Stack spacing={4}>
    <h3>Exercise Title</h3>
    <ProgressBar value={75} />
    <Stack direction="horizontal" spacing={2}>
      <Badge variant="success">Beginner</Badge>
      <Badge variant="default">15 min</Badge>
    </Stack>
    <Button variant="primary">Start</Button>
  </Stack>
</Card>

// Avoid: Custom one-off components
<CustomExerciseBox /> {/* Instead, use ExerciseCard */}
```

### Responsive Design

Use responsive utilities and mobile-first approach:

```tsx
<Grid cols={1} gap={4} className="sm:grid-cols-2 lg:grid-cols-3">
  <ExerciseCard {...props} />
</Grid>

<Container size="xl" className="px-4 md:px-6 lg:px-8">
  Content
</Container>
```

### Performance

- Import only what you need (tree-shaking)
- Use `React.memo()` for expensive components
- Leverage Tailwind's JIT compiler

### Theming

Extend or customize tokens as needed:

```tsx
// In your app
import { tokens } from '@/design-system';

const customColors = {
  ...tokens.colors,
  brand: {
    primary: '#custom-color',
  },
};
```

## Contributing

When adding new components:

1. Follow atomic design principles
2. Use TypeScript with full prop types
3. Include accessibility features
4. Add JSDoc comments
5. Update this README
6. Add examples to Storybook (if available)

## Support

For questions or issues, refer to:
- Main documentation: `/docs`
- Component examples: `/frontend/src/examples`
- Design spec: Figma (link TBD)

---

**Version:** 1.0.0
**Last Updated:** December 16, 2025
**Maintained by:** Gospel Keys Team
