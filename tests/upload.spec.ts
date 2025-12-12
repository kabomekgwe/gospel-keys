import { test, expect } from '@playwright/test';

test.describe('Upload Flow', () => {
    test.beforeEach(async ({ page }) => {
        // Mock API responses
        await page.route('*/**/api/v1/transcribe/url', async route => {
            const json = {
                job_id: 'job-123',
                status: 'queued',
                progress: 0
            };
            await route.fulfill({ json });
        });
    });

    test('validates youtube url and submits job', async ({ page }) => {
        await page.goto('/upload');

        // Check page title
        await expect(page).toHaveTitle(/Piano Keys/);
        await expect(page.getByRole('heading', { name: 'Upload' })).toBeVisible();

        // Fill URL
        const input = page.getByPlaceholder('https://www.youtube.com/watch?v=...');
        await input.fill('https://www.youtube.com/watch?v=dQw4w9WgXcQ');

        // Submit
        const submitBtn = page.getByRole('button', { name: /Start Transcription/i });
        await expect(submitBtn).toBeEnabled();
        await submitBtn.click();

        // Should redirect to jobs or show success toast
        // Assuming redirection to /jobs based on plan
        await expect(page).toHaveURL(/\/jobs/);
    });

    test('shows error for invalid url', async ({ page }) => {
        await page.goto('/upload');

        const input = page.getByPlaceholder('https://www.youtube.com/watch?v=...');
        await input.fill('invalid-url');

        // Validation message should appear
        // This depends on how validation is implemented (HTML5 or custom)
        // For now, assuming button is disabled or error shown
        const submitBtn = page.getByRole('button', { name: 'Transcribe' });
        // If button is disabled:
        // await expect(submitBtn).toBeDisabled();

        // Or if error text appears:
        await expect(page.getByText('Please enter a valid YouTube URL')).toBeVisible();
    });
});
