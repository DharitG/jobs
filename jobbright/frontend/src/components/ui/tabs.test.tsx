import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from './tabs'; // Adjust path as needed

describe('Tabs Components', () => {
  const TestTabs = ({ defaultValue = "tab1" }: { defaultValue?: string }) => (
    <Tabs defaultValue={defaultValue}>
      <TabsList>
        <TabsTrigger value="tab1">Tab 1</TabsTrigger>
        <TabsTrigger value="tab2">Tab 2</TabsTrigger>
      </TabsList>
      <TabsContent value="tab1">Content for Tab 1</TabsContent>
      <TabsContent value="tab2">Content for Tab 2</TabsContent>
    </Tabs>
  );

  it('renders triggers and shows default content initially', () => {
    render(<TestTabs defaultValue="tab1" />);
    
    const trigger1 = screen.getByRole('tab', { name: 'Tab 1' });
    const trigger2 = screen.getByRole('tab', { name: 'Tab 2' });
    const content1 = screen.getByText('Content for Tab 1');
    
    expect(trigger1).toBeInTheDocument();
    expect(trigger2).toBeInTheDocument();
    expect(content1).toBeVisible();
    expect(screen.queryByText('Content for Tab 2')).toBeNull(); // Content 2 not rendered initially

    // Check data-state for active trigger
    expect(trigger1).toHaveAttribute('data-state', 'active');
    expect(trigger2).toHaveAttribute('data-state', 'inactive');
  });

  it('switches visible content when another trigger is clicked', async () => {
    const user = userEvent.setup();
    render(<TestTabs defaultValue="tab1" />);

    const trigger1 = screen.getByRole('tab', { name: 'Tab 1' });
    const trigger2 = screen.getByRole('tab', { name: 'Tab 2' });
    const content1 = screen.getByText('Content for Tab 1');

    expect(content1).toBeVisible();
    expect(screen.queryByText('Content for Tab 2')).toBeNull();
    expect(trigger1).toHaveAttribute('data-state', 'active');
    expect(trigger2).toHaveAttribute('data-state', 'inactive');

    // Click the second trigger
    await user.click(trigger2);

    // Content 1 should disappear, Content 2 should appear
    expect(screen.queryByText('Content for Tab 1')).toBeNull(); 
    const content2 = await screen.findByText('Content for Tab 2'); // Use findByText to wait for appearance
    expect(content2).toBeVisible();

    // Check data-state updates
    expect(trigger1).toHaveAttribute('data-state', 'inactive');
    expect(trigger2).toHaveAttribute('data-state', 'active');
  });

  it('applies correct roles', () => {
    render(<TestTabs />);
    expect(screen.getByRole('tablist')).toBeInTheDocument();
    expect(screen.getAllByRole('tab')).toHaveLength(2);
    expect(screen.getByRole('tabpanel')).toBeInTheDocument(); // Only the active one should have the role
  });
});
