import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest'; // Remove useState from here
import { Switch } from './switch'; // Adjust path as needed
import React, { useState } from 'react'; // Import useState from React

describe('Switch Component', () => {
  it('renders as a button with role switch', () => {
    render(<Switch data-testid="switch-test" />);
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toBeInTheDocument();
    expect(switchElement.tagName.toLowerCase()).toBe('button');
  });

  it('reflects initial checked state via data-state attribute', () => {
    // Test unchecked state
    const { rerender } = render(<Switch data-testid="switch-test" defaultChecked={false} />);
    let switchElement = screen.getByRole('switch');
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    expect(switchElement).toHaveAttribute('aria-checked', 'false');

    // Test checked state using the 'checked' prop for controlled state
    rerender(<Switch data-testid="switch-test" checked={true} />);
    switchElement = screen.getByRole('switch');
    expect(switchElement).toHaveAttribute('data-state', 'checked');
    expect(switchElement).toHaveAttribute('aria-checked', 'true');
  });

  // Helper component for controlled switch test
  const ControlledSwitch = () => {
    const [checked, setChecked] = useState(false);
    return <Switch checked={checked} onCheckedChange={setChecked} />;
  };

  it('toggles state when clicked', async () => {
    const user = userEvent.setup();
    render(<ControlledSwitch />);
    
    const switchElement = screen.getByRole('switch');
    
    // Initial state: unchecked
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    expect(switchElement).toHaveAttribute('aria-checked', 'false');

    // Click to check
    await user.click(switchElement);
    expect(switchElement).toHaveAttribute('data-state', 'checked');
    expect(switchElement).toHaveAttribute('aria-checked', 'true');

    // Click to uncheck
    await user.click(switchElement);
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    expect(switchElement).toHaveAttribute('aria-checked', 'false');
  });

  it('applies disabled attribute and styles correctly', () => {
    render(<Switch disabled />);
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toBeDisabled();
    expect(switchElement).toHaveClass('disabled:cursor-not-allowed');
    expect(switchElement).toHaveClass('disabled:opacity-50');
  });

  it('applies additional className when provided', () => {
    const testClass = 'my-custom-switch-class';
    render(<Switch className={testClass} />);
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toHaveClass(testClass);
  });
});
