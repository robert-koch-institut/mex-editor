import { ToLabelPipe } from "./to-label-pipe";

describe("ToLabelPipe", () => {
  it("create an instance", () => {
    const pipe = new ToLabelPipe();
    expect(pipe).toBeTruthy();
  });
});
