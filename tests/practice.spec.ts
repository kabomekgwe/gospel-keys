import { test, expect } from '@playwright/test';

test.describe('Practice Flow', () => {
    test.beforeEach(async ({ page }) => {
        // Mock Song Data
        await page.route('*/**/api/v1/library/songs/song-1', async route => {
            await route.fulfill({
                json: {
                    id: 'song-1',
                    title: 'Test Song',
                    duration: 120,
                    tempo: 100,
                    favorite: false,
                    created_at: new Date().toISOString()
                }
            });
        });

        // Mock Notes Data
        await page.route('*/**/api/v1/library/songs/song-1/notes', async route => {
            await route.fulfill({ json: [] });
        });
    });

    test('loads practice mode and controls', async ({ page }) => {
        await page.goto('/library/song-1');

        // Navigate to practice tab
        await page.getByRole('tab', { name: 'Practice' }).click();

        // Verify player controls
        await expect(page.getByTitle('Play')).toBeVisible();
        await expect(page.getByText('tempo')).toBeVisible();

        // Test tempo interactions
        const tempoDisplay = page.getByText(/100%/); // Assuming 100% display
        await expect(tempoDisplay).toBeVisible();
    });
});
