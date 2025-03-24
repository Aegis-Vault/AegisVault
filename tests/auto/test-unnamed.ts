```typescript
import { Client, Provider, ProviderRegistry, Result } from "@blockstack/clarity";
import { assert } from "chai";

describe("Unchecked arithmetic operations test suite", () => {
  let provider: Provider;
  let client: Client;

  before(async () => {
    provider = await ProviderRegistry.createProvider();
    client = new Client("SP3GWX3NE58KXHESRYE4DYQ1S31PQJTCRXB3PE9SB.arithmetic-contract", "unchecked-arithmetic", provider);
  });

  it("should throw error on overflow", async () => {
    const tx = client.createTransaction({
      method: { name: "unchecked-add", args: ["u340282366920938463463374607431768211455", "u1"] }
    });
    await client.signTransaction(tx);
    const res: Result = await provider.sendTransaction(tx);
    assert.isTrue(res.isError);
    assert.equal(res.value, "Runtime Error: Arithmetic overflow error.");
  });

  it("should throw error on underflow", async () => {
    const tx = client.createTransaction({
      method: { name: "unchecked-subtract", args: ["u0", "u1"] }
    });
    await client.signTransaction(tx);
    const res: Result = await provider.sendTransaction(tx);
    assert.isTrue(res.isError);
    assert.equal(res.value, "Runtime Error: Arithmetic underflow error.");
  });

  after(async () => {
    await provider.close();
  });
});
```

This test suite checks for unchecked arithmetic operations in a hypothetical Clarity smart contract. The `unchecked-add` and `unchecked-subtract` functions are supposed to perform addition and subtraction respectively without checking for overflow and underflow. The test cases provide inputs that would cause overflow and underflow and expect the contract to throw an error.