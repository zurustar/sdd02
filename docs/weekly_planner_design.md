# Weekly Planner View Design

The weekly planner replaces the existing list-style calendar so users can see availability across the week at a glance. This document captures the expectations that should guide the implementation.

## Layout Overview

- **View span:** exactly seven consecutive days, shown from left to right. The default starting day is Monday.
- **Time axis:** vertical axis running from 06:00 to 22:00 in one-hour increments. Each hour should have a labeled row, with visual subdivision to support half-hour events.
- **Grid:** combine the day columns and time rows into a matrix. Empty cells should have a subtle background and faint borders to help users orient themselves without overwhelming the content.

## Event Blocks

- Each schedule entry is rendered as a block occupying the column of its day and spanning vertically between its start and end times.
- Show the event title prominently, with optional location and room beneath in smaller text. When space is limited, truncate with ellipsis but keep a tooltip or hover state showing the full details.
- Use a distinct background color per event owner, or fall back to a consistent accent color when ownership information is unavailable. Maintain WCAG AA contrast for text.

## Interactions

- Clicking an empty cell opens the “Create Schedule” dialog prefilled with the corresponding start time and day.
- Clicking an event opens the existing “Edit Schedule” dialog.
- Dragging an event should be scoped for a later enhancement, so ensure the markup and CSS structure will make future drag-and-drop support practical.

## Responsive Behavior

- On narrow screens (under 768px), switch to a stacked view that shows each day vertically while preserving time ordering. The desktop grid remains the canonical reference.
- Ensure horizontal scrolling is available if the weekly grid cannot fit entirely on the screen, keeping the time axis pinned for context.

## Accessibility Notes

- Provide descriptive `aria-label`s for grid cells (e.g., “Tuesday at 14:00”).
- Ensure the planner is navigable via keyboard by allowing focus on each cell and event block.
- Respect the user’s locale for date formatting once localization support is available, but keep Monday-start as the default until then.

## Visual Inspiration

Think of a traditional paper planner that shows a week spread across two pages. Aim for a clean, minimal aesthetic with clear separation between days and times, making it easy to scan for free slots.
