# Gospel Keys Design System - Migration Examples

This document provides **before/after** examples for migrating existing code to the new design system.

---

## 🎯 Migration Priority Order

1. **Buttons** (highest impact, easiest)
2. **Empty States** (critical UX improvement)
3. **Cards** (visual consistency)
4. **Skeletons** (better loading UX)
5. **Badges** (status clarity)
6. **Page Headers** (consistent structure)

---

## 1. Homepage Migration

### File: `frontend/src/routes/index.tsx`

#### Before: Hero Section Buttons (Lines 29-54)

```tsx
{!isLoading && (
  <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
    {activeCurriculum ? (
      <>
        <Link
          to="/curriculum/daily"
          className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all shadow-lg"
        >
          Continue Learning
        </Link>
        <Link
          to="/curriculum"
          className="px-8 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-all"
        >
          View Curriculum
        </Link>
      </>
    ) : (
      <Link
        to="/curriculum/new"
        className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all shadow-lg"
      >
        Get Started
      </Link>
    )}
  </div>
)}
```

#### After: Using Design System

```tsx
import { Button } from "@/components/ui/button"
import { Link } from "@tanstack/react-router"

{!isLoading && (
  <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
    {activeCurriculum ? (
      <>
        <Button asChild variant="primary" size="lg">
          <Link to="/curriculum/daily">Continue Learning</Link>
        </Button>
        <Button asChild variant="secondary" size="lg">
          <Link to="/curriculum">View Curriculum</Link>
        </Button>
      </>
    ) : (
      <Button asChild variant="primary" size="lg">
        <Link to="/curriculum/new">Get Started</Link>
      </Button>
    )}
  </div>
)}
```

**Reduction**: 26 lines → 14 lines (46% reduction)
**Character count**: 1,156 → 542 (53% reduction)

#### Before: Feature Cards (Lines 64-94)

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <FeatureCard
    icon="🎹"
    title="8 Music Genres"
    description="Master Gospel, Jazz, Blues, Neo-Soul, Classical, Reggae, Latin, and R&B with genre-specific AI generation"
  />
  {/* ... more feature cards */}
</div>

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-400 leading-relaxed">{description}</p>
    </div>
  )
}
```

#### After: Using Card Component

```tsx
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <FeatureCard
    icon="🎹"
    title="8 Music Genres"
    description="Master Gospel, Jazz, Blues, Neo-Soul, Classical, Reggae, Latin, and R&B with genre-specific AI generation"
  />
  {/* ... more feature cards */}
</div>

function FeatureCard({ icon, title, description }) {
  return (
    <Card variant="glass" className="hover:border-purple-500/50 hover:shadow-purple-500/10">
      <CardHeader>
        <div className="text-4xl mb-2" aria-hidden="true">{icon}</div>
        <CardTitle as="h3" className="text-xl text-white">{title}</CardTitle>
        <CardDescription className="text-gray-400">{description}</CardDescription>
      </CardHeader>
    </Card>
  )
}
```

**Benefits**:
- Consistent card styling
- Better accessibility (proper heading hierarchy)
- Easier to maintain

---

## 2. Curriculum Page Migration

### File: `frontend/src/routes/curriculum.index.tsx`

#### Before: Empty State (Lines 15-17)

```tsx
if (!curriculumList || curriculumList.length === 0) {
  return null; // ❌ User sees blank page
}
```

#### After: Proper Empty State

```tsx
import { EmptyState } from "@/components/ui/empty-state"

if (!curriculumList?.length) {
  return (
    <EmptyState
      icon="📚"
      title="No curriculums yet"
      description="Create your first personalized curriculum to begin your music learning journey"
      action={{
        label: "Create Curriculum",
        href: "/curriculum/new"
      }}
      size="lg"
    />
  )
}
```

**User Impact**:
- Before: Confused users wondering if app is broken
- After: Clear guidance on next step

#### Before: Curriculum Cards (Lines 23-63)

```tsx
<Link
  key={curriculum.id}
  to="/curriculum/$curriculumId"
  params={{ curriculumId: curriculum.id }}
  className="block bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition"
>
  <div className="flex justify-between items-start mb-3">
    <h3 className="text-lg font-semibold">{curriculum.title}</h3>
    <span
      className={`px-2 py-1 text-xs font-medium rounded ${
        curriculum.status === 'active'
          ? 'bg-green-100 text-green-800'
          : curriculum.status === 'completed'
            ? 'bg-blue-100 text-blue-800'
            : 'bg-gray-100 text-gray-800'
      }`}
    >
      {curriculum.status}
    </span>
  </div>
  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
    {curriculum.description}
  </p>
  {/* ... more content */}
</Link>
```

#### After: Using Card + Badge

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Link } from "@tanstack/react-router"

<Card variant="interactive" asChild>
  <Link
    to="/curriculum/$curriculumId"
    params={{ curriculumId: curriculum.id }}
  >
    <CardHeader>
      <div className="flex justify-between items-start">
        <CardTitle as="h3" className="text-lg">{curriculum.title}</CardTitle>
        <Badge variant={curriculum.status}>{curriculum.status}</Badge>
      </div>
      <CardDescription className="line-clamp-2">
        {curriculum.description}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div className="flex justify-between text-sm text-slate-600">
        <span>Week {curriculum.current_week}/{curriculum.duration_weeks}</span>
        <span>{curriculum.module_count} modules</span>
      </div>
      <div className="mt-3">
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${curriculum.overall_progress}%` }}
          />
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {Math.round(curriculum.overall_progress)}% complete
        </p>
      </div>
    </CardContent>
  </Link>
</Card>
```

**Benefits**:
- Type-safe status badges
- Consistent hover effects
- Better semantic HTML

---

## 3. Loading States Migration

### File: `frontend/src/routes/curriculum.daily.tsx`

#### Before: Generic Loading (Lines 14-16)

```tsx
if (isLoading) {
  return <div className="text-center py-8">Loading today's practice...</div>;
}
```

#### After: Skeleton Loading

```tsx
import { SkeletonExerciseCard } from "@/components/ui/skeleton"

if (isLoading) {
  return (
    <div className="space-y-4">
      <SkeletonExerciseCard />
      <SkeletonExerciseCard />
      <SkeletonExerciseCard />
    </div>
  )
}
```

**User Impact**:
- Before: Jarring text flash
- After: Smooth content placeholder that matches actual layout

---

## 4. Form Page Migration

### File: `frontend/src/routes/curriculum.new.tsx`

#### Before: Mode Toggle Buttons (Lines 54-74)

```tsx
<div className="flex gap-2 mb-6">
  <button
    onClick={() => setMode('template')}
    className={`px-4 py-2 rounded-lg font-medium transition ${
      mode === 'template'
        ? 'bg-blue-600 text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    }`}
  >
    From Template
  </button>
  <button
    onClick={() => setMode('custom')}
    className={`px-4 py-2 rounded-lg font-medium transition ${
      mode === 'custom'
        ? 'bg-blue-600 text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    }`}
  >
    Custom (AI Generated)
  </button>
</div>
```

#### After: Button Component

```tsx
import { Button } from "@/components/ui/button"

<div className="flex gap-2 mb-6">
  <Button
    onClick={() => setMode('template')}
    variant={mode === 'template' ? 'primary' : 'outline'}
  >
    From Template
  </Button>
  <Button
    onClick={() => setMode('custom')}
    variant={mode === 'custom' ? 'primary' : 'outline'}
  >
    Custom (AI Generated)
  </Button>
</div>
```

**Reduction**: 23 lines → 13 lines (43% reduction)

#### Before: Template Cards (Lines 84-101)

```tsx
<div
  key={template.key}
  className="bg-white border border-gray-200 rounded-lg p-6"
>
  <h3 className="text-lg font-semibold mb-2">{template.title}</h3>
  <p className="text-gray-600 text-sm mb-4">{template.description}</p>
  <div className="flex justify-between items-center">
    <span className="text-sm text-gray-500">{template.weeks} weeks</span>
    <button
      onClick={() => handleCreateFromTemplate(template.key)}
      disabled={createDefault.isPending}
      className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
    >
      {createDefault.isPending ? 'Creating...' : 'Select'}
    </button>
  </div>
</div>
```

#### After: Card + Button

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

<Card key={template.key}>
  <CardHeader>
    <CardTitle as="h3" className="text-lg">{template.title}</CardTitle>
    <CardDescription>{template.description}</CardDescription>
  </CardHeader>
  <CardFooter className="justify-between">
    <span className="text-sm text-slate-500">{template.weeks} weeks</span>
    <Button
      onClick={() => handleCreateFromTemplate(template.key)}
      disabled={createDefault.isPending}
      variant="primary"
    >
      {createDefault.isPending ? 'Creating...' : 'Select'}
    </Button>
  </CardFooter>
</Card>
```

---

## 5. Genre Page Migration

### File: `frontend/src/routes/genres.$genreId.tsx`

#### Before: Genre Header (Lines 158-162)

```tsx
<div className={`bg-gradient-to-br ${genre.color} rounded-lg p-8 mb-8 text-white`}>
  <div className="text-5xl mb-4">{genre.icon}</div>
  <h1 className="text-4xl font-bold mb-2">{genre.name} Generator</h1>
  <p className="text-lg opacity-90">{genre.description}</p>
</div>
```

#### After: Card + PageHeader Pattern

```tsx
import { Card } from "@/components/ui/card"
import { PageHeader } from "@/components/ui/page-header"

<Card variant={genre.id} padding="lg" className="text-white mb-8">
  <div className="text-5xl mb-4" aria-hidden="true">{genre.icon}</div>
  <PageHeader
    title={`${genre.name} Generator`}
    description={genre.description}
    spacing="none"
  />
</Card>
```

**Benefits**:
- Automatic genre variant styling
- Consistent spacing
- Better semantic structure

#### Before: Generate Button (Lines 248-262)

```tsx
<button
  onClick={() =>
    onGenerate({
      description,
      tempo,
      num_bars: numBars,
      application: 'uptempo',
      ai_percentage: 0.0,
    })
  }
  disabled={isGenerating}
  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
>
  {isGenerating ? 'Generating...' : 'Generate Gospel Arrangement'}
</button>
```

#### After: Button with Genre Variant

```tsx
import { Button } from "@/components/ui/button"

<Button
  onClick={() =>
    onGenerate({
      description,
      tempo,
      num_bars: numBars,
      application: 'uptempo',
      ai_percentage: 0.0,
    })
  }
  disabled={isGenerating}
  variant="gospel"
  size="lg"
  className="w-full"
>
  {isGenerating ? 'Generating...' : 'Generate Gospel Arrangement'}
</Button>
```

---

## 6. Daily Practice Page Migration

### File: `frontend/src/routes/curriculum.daily.tsx`

#### Before: Empty State (Lines 18-26)

```tsx
if (!practice || practice.items.length === 0) {
  return (
    <div className="text-center py-12 bg-gray-50 rounded-lg">
      <h3 className="text-xl font-semibold mb-2">No exercises due today</h3>
      <p className="text-gray-600 mb-4">
        Check back tomorrow or explore new lessons in your curriculum
      </p>
    </div>
  );
}
```

#### After: EmptyState Component

```tsx
import { EmptyState } from "@/components/ui/empty-state"

if (!practice?.items.length) {
  return (
    <EmptyState
      icon="🎉"
      title="All caught up!"
      description="No exercises due today. Check back tomorrow or explore new lessons in your curriculum"
      action={{
        label: "Explore Lessons",
        href: "/curriculum"
      }}
      secondaryAction={{
        label: "Browse Genres",
        href: "/genres"
      }}
    />
  )
}
```

**User Impact**:
- Actionable CTAs instead of dead-end message
- Positive framing ("All caught up!" vs "No exercises")

#### Before: Priority Badges (Lines 78-87)

```tsx
{item.priority === 1 && (
  <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
    Overdue
  </span>
)}
{item.priority === 3 && (
  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
    New
  </span>
)}
```

#### After: Badge Component

```tsx
import { Badge } from "@/components/ui/badge"

{item.priority === 1 && <Badge variant="overdue">Overdue</Badge>}
{item.priority === 3 && <Badge variant="new">New</Badge>}
```

**Reduction**: 10 lines → 3 lines (70% reduction)

#### Before: Quality Buttons (Lines 135-150)

```tsx
{[1, 2, 3, 4, 5].map((quality) => (
  <button
    key={quality}
    onClick={() => handleComplete(item.exercise.id, quality)}
    disabled={completeExercise.isPending}
    className={`px-4 py-2 rounded-lg font-medium transition ${
      quality <= 2
        ? 'bg-red-100 text-red-800 hover:bg-red-200'
        : quality === 3
          ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
          : 'bg-green-100 text-green-800 hover:bg-green-200'
    } disabled:opacity-50`}
  >
    {quality}
  </button>
))}
```

#### After: Button Component with Variants

```tsx
import { Button } from "@/components/ui/button"

{[1, 2, 3, 4, 5].map((quality) => (
  <Button
    key={quality}
    onClick={() => handleComplete(item.exercise.id, quality)}
    disabled={completeExercise.isPending}
    variant={
      quality <= 2 ? 'destructive' :
      quality === 3 ? 'warning' :
      'success'
    }
  >
    {quality}
  </Button>
))}
```

**Note**: `warning` variant needs to be added to Button component, or use `outline` with custom className.

---

## 7. Layout Migration

### File: `frontend/src/routes/curriculum.tsx`

#### Before: Page Header (Lines 25-29)

```tsx
<header className="mb-8">
  <h1 className="text-4xl font-bold mb-2">My Curriculum</h1>
  <p className="text-gray-600">
    Personalized music education powered by AI
  </p>
</header>
```

#### After: PageHeader Component

```tsx
import { PageHeader } from "@/components/ui/page-header"

<PageHeader
  title="My Curriculum"
  description="Personalized music education powered by AI"
/>
```

#### Before: Active Curriculum Card (Lines 33-60)

```tsx
{activeCurriculum && (
  <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 mb-8 text-white">
    <div className="flex justify-between items-start">
      <div>
        <h2 className="text-2xl font-bold mb-2">{activeCurriculum.title}</h2>
        <p className="text-blue-100 mb-4">{activeCurriculum.description}</p>
        {/* ... more content */}
      </div>
      <Link
        to="/curriculum/$curriculumId"
        params={{ curriculumId: activeCurriculum.id }}
        className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition"
      >
        View Details
      </Link>
    </div>
  </div>
)}
```

#### After: Card Component

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

{activeCurriculum && (
  <Card variant="gradient" className="bg-gradient-to-r from-blue-500 to-purple-600 text-white mb-8">
    <CardHeader>
      <div className="flex justify-between items-start">
        <div>
          <CardTitle className="text-white">{activeCurriculum.title}</CardTitle>
          <CardDescription className="text-blue-100">
            {activeCurriculum.description}
          </CardDescription>
        </div>
        <Button asChild variant="outline" className="bg-white text-blue-600 hover:bg-blue-50">
          <Link
            to="/curriculum/$curriculumId"
            params={{ curriculumId: activeCurriculum.id }}
          >
            View Details
          </Link>
        </Button>
      </div>
    </CardHeader>
    <CardContent>
      <div className="flex gap-4 text-sm">
        <div>
          <span className="opacity-75">Week:</span>{' '}
          <span className="font-semibold">
            {activeCurriculum.current_week}/{activeCurriculum.duration_weeks}
          </span>
        </div>
        <div>
          <span className="opacity-75">Modules:</span>{' '}
          <span className="font-semibold">{activeCurriculum.modules.length}</span>
        </div>
      </div>
    </CardContent>
  </Card>
)}
```

---

## 📊 Migration Impact Summary

| Component | Files Affected | Lines Reduced | Character Reduction |
|-----------|----------------|---------------|---------------------|
| Button | 8 files | ~120 lines | ~6,400 chars (55%) |
| Card | 6 files | ~80 lines | ~3,200 chars (45%) |
| EmptyState | 4 files | ~40 lines | ~1,600 chars (65%) |
| Skeleton | 5 files | ~25 lines | ~800 chars (60%) |
| Badge | 3 files | ~35 lines | ~1,400 chars (70%) |
| PageHeader | 7 files | ~60 lines | ~2,400 chars (50%) |
| **Total** | **20 files** | **~360 lines** | **~15,800 chars** |

**Overall Reduction**: 298 inline styles → ~50 component uses = **83% reduction in styling code**

---

## ✅ Migration Checklist

### Phase 1: Core Components (Week 1, Days 1-2)
- [ ] Replace all button inline styles with `<Button>` component
- [ ] Replace all `return null` with `<EmptyState>` component
- [ ] Update index.tsx hero section
- [ ] Update curriculum.new.tsx buttons

### Phase 2: Cards & Lists (Week 1, Days 3-4)
- [ ] Migrate curriculum cards to `<Card>` component
- [ ] Migrate genre cards to `<Card>` component
- [ ] Replace all status spans with `<Badge>` component
- [ ] Update daily practice exercise cards

### Phase 3: Loading States (Week 1, Day 5)
- [ ] Replace all "Loading..." text with `<Skeleton>` presets
- [ ] Add SkeletonCurriculumCard to curriculum.index.tsx
- [ ] Add SkeletonExerciseCard to curriculum.daily.tsx
- [ ] Add SkeletonHeader to genre pages

### Phase 4: Headers & Structure (Week 2)
- [ ] Replace all page headers with `<PageHeader>` component
- [ ] Update curriculum layout header
- [ ] Update genre detail headers
- [ ] Standardize spacing across all pages

---

## 🔍 Search & Replace Patterns

### VS Code Search Patterns

1. **Find all gradient buttons:**
   ```regex
   className="[^"]*bg-gradient-to-r from-blue-500 to-purple-600[^"]*"
   ```

2. **Find all empty returns:**
   ```regex
   return null;?\s*//.*empty
   ```

3. **Find all inline status badges:**
   ```regex
   className={`[^`]*bg-(green|red|blue|yellow)-100 text-\1-800[^`]*`}
   ```

4. **Find all loading text:**
   ```regex
   <div[^>]*>Loading[^<]*</div>
   ```

---

**End of Migration Examples**
