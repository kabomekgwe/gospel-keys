# Curriculum New Page Redesign - Standalone Experience

## Problem

When clicking "Create New" from `/curriculum`, the `/curriculum/new` page was showing the same hero card, stats, and navigation tabs as the parent layout. This made it unclear that the user was now in the creation flow.

## Solution

Made `/curriculum/new` a **standalone page experience** with clear visual separation from the main curriculum view.

## Changes Applied

### 1. Conditional Layout in Parent Route

**File:** `frontend/src/routes/curriculum.tsx`

**Changes:**
- Added `useLocation` hook to detect current route
- Added conditional rendering: if on `/curriculum/new`, render only the outlet without hero card/tabs
- This prevents layout inheritance for the creation page

```tsx
const isCreatingNew = location.pathname === '/curriculum/new';

// If creating new curriculum, just render the outlet without the layout
if (isCreatingNew) {
  return (
    <div className="px-6 py-8">
      <Outlet />
    </div>
  );
}
```

### 2. Enhanced `/curriculum/new` Page Design

**File:** `frontend/src/routes/curriculum.new.tsx`

**New Features:**

#### Back Button
```tsx
<Link to="/curriculum" className="...">
  <ArrowLeft className="size-4" />
  Back to curriculum
</Link>
```

#### Page Header
- Clear title: "Create New Curriculum"
- Descriptive subtitle: "Choose a template or generate a personalized curriculum with AI"

#### Redesigned Mode Toggle
- Uses design system `Button` component
- Icons for visual distinction:
  - 📄 `FileText` for Template mode
  - ✨ `Sparkles` for AI Generated mode
- Full-width responsive buttons

#### Template Cards (Redesigned)
- Now uses `Card` component from design system
- Structured layout with:
  - `CardHeader` - Title and description
  - `CardContent` - Duration with clock icon
  - `CardFooter` - "Select Template" button
- Hover effects and shadows
- Consistent spacing

#### Custom Generation Form (Redesigned)
- Wrapped in `Card` component
- Clean card structure:
  - `CardHeader` - Title and description
  - `CardContent` - Form fields
  - `CardFooter` - Generate button
- Styled input fields with dark mode support
- Purple-themed info box with Sparkles icon
- Large, prominent "Generate Curriculum" button

## Visual Differences

### Before:
- `/curriculum/new` showed hero card, stats cards, and navigation tabs
- User couldn't tell they were in creation mode
- Same purple gradient background covered content

### After:
- `/curriculum/new` is a clean, standalone page
- Clear "Back to curriculum" link at top
- Distinct page header
- Professional card-based layout
- No hero card or navigation tabs visible
- Clear visual separation from main curriculum view

## User Flow

1. **From `/curriculum`:**
   - User sees their curriculums with hero card and tabs
   - Clicks "Create New" button

2. **Navigates to `/curriculum/new`:**
   - Hero card and tabs disappear (clean slate)
   - Page header shows "Create New Curriculum"
   - Back button visible at top
   - Two large toggle buttons for mode selection

3. **Template Mode:**
   - Grid of professional template cards
   - Each card shows title, description, duration
   - "Select Template" button at bottom

4. **AI Generated Mode:**
   - Single card form with title and duration inputs
   - Purple info box explaining AI generation
   - Large "Generate Curriculum" button

5. **After Creation:**
   - Toast notification shows success
   - Redirects to `/curriculum/{id}` page

## Design System Components Used

✅ `PageHeader` - Consistent page titles
✅ `Button` - Mode toggles and actions
✅ `Card` with variants - Template cards and form
✅ `Badge` - (ready for status indicators)
✅ Icons from `lucide-react` - Visual hierarchy

## Files Modified

1. ✅ `frontend/src/routes/curriculum.tsx`
   - Added conditional layout rendering
   - Imported `useLocation`

2. ✅ `frontend/src/routes/curriculum.new.tsx`
   - Added back button
   - Added PageHeader
   - Redesigned mode toggle with Button components
   - Converted template cards to Card components
   - Converted custom form to Card component
   - Added icons for better UX

## Result

The `/curriculum/new` page now provides a **clear, focused creation experience** that's visually distinct from the main curriculum view. Users can immediately tell they're in creation mode and have a clean interface to work with.

**Status:** ✅ **Complete and Ready to Test**
