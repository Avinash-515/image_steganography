import fs from 'fs';
import readline from 'readline';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🚀 Smart Contract Deployment Setup');
console.log('=====================================\n');

console.log('To deploy the contract, you need:');
console.log('1. Infura Project ID (free at https://infura.io/)');
console.log('2. Private Key with Sepolia ETH (get from https://sepoliafaucet.com/)');
console.log('3. Contract will be deployed to Sepolia testnet\n');

rl.question('Do you have these ready? (y/n): ', (answer) => {
  if (answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes') {
    console.log('\n📝 Please create a .env file in the project root with:');
    console.log('INFURA_PROJECT_ID=your_infura_project_id');
    console.log('PRIVATE_KEY=your_private_key');
    console.log('\nThen run: npm run deploy');
  } else {
    console.log('\n📋 Setup Steps:');
    console.log('1. Go to https://infura.io/ and create a free account');
    console.log('2. Create a new project and copy your Project ID');
    console.log('3. Get Sepolia ETH from https://sepoliafaucet.com/');
    console.log('4. Create .env file with your credentials');
    console.log('5. Run: npm run deploy');
  }
  
  rl.close();
});
