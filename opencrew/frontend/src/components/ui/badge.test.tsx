import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge, badgeVariants } from './badge'; // Adjust path as needed

describe('Badge Component', () => {
  it('renders with default variant and base styles', () => {
    render(<Badge>Default Badge</Badge>);
    const badge = screen.getByText('Default Badge');
    expect(badge).toBeInTheDocument();
    // Check for key base classes from design system
    expect(badge).toHaveClass('inline-flex');
    expect(badge).toHaveClass('items-center');
    expect(badge).toHaveClass('rounded-full');
    expect(badge).toHaveClass('border');
    expect(badge).toHaveClass('px-2.5');
    expect(badge).toHaveClass('py-0.5');
    expect(badge).toHaveClass('text-xs');
    expect(badge).toHaveClass('font-semibold');
    expect(badge).toHaveClass('uppercase');
    // Check for default variant class (example)
    expect(badge).toHaveClass('bg-primary'); 
  });

  // Test each variant
  const variants: Array<React.ComponentProps<typeof Badge>['variant']> = [
    'default', 
    'secondary', 
    'destructive', 
    'outline', 
    'success', 
    'warning', 
    'info'
  ];

  variants.forEach((variant) => {
    // Skip undefined variant case which might happen if variant prop is optional
    if (!variant) return; 

    it(`applies correct classes for variant: ${variant}`, () => {
      render(<Badge variant={variant}>{`${variant} Badge`}</Badge>);
      const badge = screen.getByText(`${variant} Badge`);
      // Check if the generated class list includes the expected variant class pattern
      // This is less brittle than checking the exact output of badgeVariants
      const expectedClassSubstring = badgeVariants({ variant }).split(' ').pop(); // Get the last class, often the most specific one
      expect(badge.className).toEqual(expect.stringContaining(expectedClassSubstring || ''));

      // Spot check specific background/text colors based on design system mapping
      if (variant === 'destructive') expect(badge).toHaveClass('bg-destructive');
      if (variant === 'success') expect(badge).toHaveClass('bg-accent');
      if (variant === 'warning') expect(badge).toHaveClass('bg-warning');
      if (variant === 'info') expect(badge).toHaveClass('bg-primary-500');
      if (variant === 'outline') expect(badge).toHaveClass('text-foreground');
    });
  });

  it('applies additional className when provided', () => {
    const testClass = 'my-custom-badge-class';
    render(<Badge className={testClass}>Custom Class</Badge>);
    const badge = screen.getByText('Custom Class');
    expect(badge).toHaveClass(testClass);
  });
});
