import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Button, buttonVariants } from './button'; // Adjust path as needed
import { Slot } from '@radix-ui/react-slot';
import React from 'react';

describe('Button Component', () => {
  it('renders with default variant and size', () => {
    render(<Button>Click Me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    // Check for a couple of key default classes (can't check all due to dynamic generation)
    expect(button).toHaveClass('bg-primary-500'); 
    expect(button).toHaveClass('text-white');
    expect(button).toHaveClass('h-9'); // Default size height
  });

  // Test each variant
  const variants: Array<React.ComponentProps<typeof Button>['variant']> = [
    'default', 
    'destructive', 
    'outline', 
    'ghost', 
    'link',
    'secondary' // Include the original secondary for completeness
  ];

  variants.forEach((variant) => {
    it(`applies correct classes for variant: ${variant}`, () => {
      render(<Button variant={variant}>Variant Test</Button>);
      const button = screen.getByRole('button', { name: /variant test/i });
      // We rely on buttonVariants internal logic being correct.
      // Spot check a key class for some variants to ensure the variant is applied.
      if (variant === 'destructive') expect(button).toHaveClass('bg-error');
      if (variant === 'outline') expect(button).toHaveClass('border-primary-500');
      if (variant === 'ghost') expect(button).toHaveClass('hover:bg-primary-500/10');
      if (variant === 'link') expect(button).toHaveClass('text-primary-500');
    });
  });

  // Test each size
  const sizes: Array<React.ComponentProps<typeof Button>['size']> = [
    'default', 
    'sm', 
    'lg', 
    'icon'
  ];

  sizes.forEach((size) => {
    it(`applies correct classes for size: ${size}`, () => {
      render(<Button size={size}>Size Test</Button>);
      const button = screen.getByRole('button', { name: /size test/i });
       // Spot check height class to ensure the size is applied.
       if (size === 'sm') expect(button).toHaveClass('h-8');
       if (size === 'lg') expect(button).toHaveClass('h-10');
       if (size === 'icon') expect(button).toHaveClass('size-9');
    });
  });

  it('renders as child element when asChild prop is true', () => {
    render(
      <Button asChild>
        <a href="/">Link Button</a>
      </Button>
    );
    // Check if it renders as an anchor tag instead of a button
    const linkElement = screen.getByRole('link', { name: /link button/i });
    expect(linkElement).toBeInTheDocument();
    expect(linkElement.tagName.toLowerCase()).toBe('a');
    // Check if button classes are still applied
    expect(linkElement).toHaveClass('bg-primary-500'); // Default variant classes
  });

  it('applies disabled attribute and styles correctly', () => {
    render(<Button disabled>Disabled Button</Button>);
    const button = screen.getByRole('button', { name: /disabled button/i });
    expect(button).toBeDisabled();
    expect(button).toHaveClass('disabled:opacity-50');
  });
});
