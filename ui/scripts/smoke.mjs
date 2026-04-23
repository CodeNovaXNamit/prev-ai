const backendBase = process.env.SMOKE_BACKEND_URL ?? "http://backend:8000";
const frontendBase = process.env.SMOKE_FRONTEND_URL ?? "http://frontend:3000";

async function assertOk(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }
  console.log(`OK ${url}`);
}

async function main() {
  await assertOk(`${backendBase}/health`);
  await assertOk(`${frontendBase}/`);
  await assertOk(`${frontendBase}/chat`);
  await assertOk(`${frontendBase}/dashboard`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
