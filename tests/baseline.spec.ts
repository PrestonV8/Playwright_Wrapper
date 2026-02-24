import {test, expect} from "@playwright/test";

test("baseline", async () => {
    expect(1 + 1).toBe(2);
});