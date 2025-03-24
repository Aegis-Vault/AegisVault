import { execSync } from 'child_process';

beforeAll(() => {
  console.log('🔧 Deploying Clarity contracts before tests...');
  execSync('clarinet integrate', { stdio: 'inherit' });
});