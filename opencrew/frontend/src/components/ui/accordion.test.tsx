import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from './accordion'; // Adjust path as needed
import type * as AccordionPrimitive from "@radix-ui/react-accordion" // Import Radix types

describe('Accordion Components', () => {

  // Removed the TestAccordion helper component

  it('renders triggers and hides content initially (default type="single")', () => {
    render(
      <Accordion type="single" collapsible>
        <AccordionItem value="item-1">
          <AccordionTrigger>Trigger 1</AccordionTrigger>
          <AccordionContent>Content 1</AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2">
          <AccordionTrigger>Trigger 2</AccordionTrigger>
          <AccordionContent>Content 2</AccordionContent>
        </AccordionItem>
      </Accordion>
    );
    expect(screen.getByText('Trigger 1')).toBeInTheDocument();
    expect(screen.getByText('Trigger 2')).toBeInTheDocument();
    // Check that content is not rendered initially
    expect(screen.queryByText('Content 1')).toBeNull();
    expect(screen.queryByText('Content 2')).toBeNull(); 
  });

  it('shows content when trigger is clicked (type="single")', async () => {
    const user = userEvent.setup();
    render(
      <Accordion type="single" collapsible>
        <AccordionItem value="item-1">
          <AccordionTrigger>Trigger 1</AccordionTrigger>
          <AccordionContent>Content 1</AccordionContent>
        </AccordionItem>
      </Accordion>
    );
    
    const trigger1 = screen.getByText('Trigger 1');
    // Content shouldn't be there yet
    expect(screen.queryByText('Content 1')).toBeNull();

    await user.click(trigger1);
    // Now find the content after click
    const content1 = await screen.findByText('Content 1'); 
    expect(content1).toBeVisible();
  });

  it('switches visible content when another trigger is clicked (type="single")', async () => {
    const user = userEvent.setup();
    render(
      <Accordion type="single" collapsible defaultValue="item-1">
        <AccordionItem value="item-1">
          <AccordionTrigger>Trigger 1</AccordionTrigger>
          <AccordionContent>Content 1</AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2">
          <AccordionTrigger>Trigger 2</AccordionTrigger>
          <AccordionContent>Content 2</AccordionContent>
        </AccordionItem>
      </Accordion>
    );

    // const trigger1 = screen.getByText('Trigger 1'); // Not needed for this test logic
    const content1 = screen.getByText('Content 1'); // Content 1 is visible by default
    const trigger2 = screen.getByText('Trigger 2');
    // Content 2 should not be in the DOM initially
    expect(screen.queryByText('Content 2')).toBeNull(); 

    expect(content1).toBeVisible();

    await user.click(trigger2);

    // Content 1 should disappear, Content 2 should appear
    expect(screen.queryByText('Content 1')).toBeNull(); 
    const content2 = await screen.findByText('Content 2');
    expect(content2).toBeVisible();
    
    // Clicking again should close it (collapsible=true)
    await user.click(trigger2);
    expect(screen.queryByText('Content 2')).toBeNull();
  });
  
  it('allows multiple items open when type="multiple"', async () => {
    const user = userEvent.setup();
    render(
      // Remove collapsible prop when type="multiple"
      <Accordion type="multiple"> 
        <AccordionItem value="item-1">
          <AccordionTrigger>Trigger 1</AccordionTrigger>
          <AccordionContent>Content 1</AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2">
          <AccordionTrigger>Trigger 2</AccordionTrigger>
          <AccordionContent>Content 2</AccordionContent>
        </AccordionItem>
      </Accordion>
    );
    
    const trigger1 = screen.getByText('Trigger 1');
    const trigger2 = screen.getByText('Trigger 2');

    // Content shouldn't be there yet
    expect(screen.queryByText('Content 1')).toBeNull();
    expect(screen.queryByText('Content 2')).toBeNull();

    await user.click(trigger1);
    const content1 = await screen.findByText('Content 1');
    expect(content1).toBeVisible();
    expect(screen.queryByText('Content 2')).toBeNull(); // Content 2 still not visible

    await user.click(trigger2);
    const content2 = await screen.findByText('Content 2');
    expect(screen.getByText('Content 1')).toBeVisible(); // Content 1 should remain visible
    expect(content2).toBeVisible(); 
  });
});
