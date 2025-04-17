import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DailyStreak } from './DailyStreak'; // Adjust path as needed

describe('DailyStreak Component', () => {
  it('renders the initial streak count correctly', () => {
    const initialStreak = 5;
    render(<DailyStreak initialStreak={initialStreak} />);

    // Check if the streak number is displayed
    const streakNumber = screen.getByText(initialStreak.toString());
    expect(streakNumber).toBeInTheDocument();

    // Check if the "days" text is displayed
    const daysText = screen.getByText('days');
    expect(daysText).toBeInTheDocument();
  });

  it('renders 0 when no initial streak is provided', () => {
    render(<DailyStreak />);

    const streakNumber = screen.getByText('0');
    expect(streakNumber).toBeInTheDocument();
  });

  it('renders the flame icon', () => {
    render(<DailyStreak initialStreak={3} />);
    
    // Check for the presence of the icon (using title or role might be better if available)
    // For now, we check if an SVG element is rendered within the component scope.
    // A more robust test might involve checking the icon's path data or adding a test ID.
    const icon = screen.getByRole('img', { hidden: true }); // Lucide icons might not have accessible roles by default
    expect(icon).toBeInTheDocument(); 
  });

  // TODO: Add tests for loading and error states when tRPC query is implemented
  // TODO: Add tests for icon color change based on streak > 0
});
