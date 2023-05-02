from click.testing import CliRunner
from download_esm.cli import cli
import pathlib
import pytest


@pytest.mark.parametrize("use_directory", (True, False))
def test_download_esm(mocks, use_directory):
    runner = CliRunner()
    with runner.isolated_filesystem():
        args = ["@observablehq/plot"]
        if use_directory:
            args.append("js")
        result = runner.invoke(cli, args)
        assert result.exit_code == 0
        # Check files were downloaded
        path = "."
        if use_directory:
            path = "js"
        files = {p.name for p in pathlib.Path(path).glob("**/*.js")}
        assert files == {
            "observablehq-plot-0-6-6-src-index-js.js",
            "d3-array-3-2-3m.js",
            "isoformat-0-2-1m.js",
            "d3-7-8-4m.js",
        }
        # Check that code was rewritten
        rewritten_plot = (
            pathlib.Path(path) / "observablehq-plot-0-6-6-src-index-js.js"
        ).read_text()
        assert (
            'import {ascending as t,descending as n,least as $r} from "./d3-7-8-4m.js"'
            in rewritten_plot
        )
        assert (
            'import {parse as Mr,format as Lr} from "./isoformat-0-2-1m.js"'
            in rewritten_plot
        )
        # Check d3 too
        rewritten_d3 = (pathlib.Path(path) / "d3-7-8-4m.js").read_text()
        assert 'export * from "./d3-array-3-2-3m.js";' in rewritten_d3


@pytest.fixture
def mocks(httpx_mock):
    # Observable Plot
    httpx_mock.add_response(
        url="https://cdn.jsdelivr.net/npm/@observablehq/plot/+esm",
        text="""
/**
 * Bundled by jsDelivr using Rollup v2.79.1 and Terser v5.17.1.
 * Original file: /npm/@observablehq/plot@0.6.6/src/index.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
import{ascending as t,descending as n,least as $r}from"/npm/d3@7.8.4/+esm";import{parse as Mr,format as Lr}from"/npm/isoformat@0.2.1/+esm";function Er(t){return null}
//# sourceMappingURL=/sm/01413fe1f7a8c2da69e83bcc6c3f16a63658e3f27f5a8ffeda7da895d71e4aa2.map
    """,
    )
    # d3
    httpx_mock.add_response(
        url="https://cdn.jsdelivr.net/npm/d3@7.8.4/+esm",
        text="""
/**
 * Bundled by jsDelivr using Rollup v2.74.1 and Terser v5.15.1.
 * Original file: /npm/d3@7.8.4/src/index.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
export*from"/npm/d3-array@3.2.3/+esm";
""",
    )
    # isoformat
    httpx_mock.add_response(
        url="https://cdn.jsdelivr.net/npm/isoformat@0.2.1/+esm",
        text="""
/**
 * Bundled by jsDelivr using Rollup v2.74.1 and Terser v5.15.1.
 * Original file: /npm/isoformat@0.2.1/src/index.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
function t(t,n){};
//# sourceMappingURL=/sm/83fe3f74d02cac187ee0f8c70305b5a8a44813bc43c57abfb7582eb11b5b40df.map
""",
    )
    # d3-array
    httpx_mock.add_response(
        url="https://cdn.jsdelivr.net/npm/d3-array@3.2.3/+esm",
        text="""
/**
 * Bundled by jsDelivr using Rollup v2.74.1 and Terser v5.15.1.
 * Original file: /npm/d3-array@3.2.3/src/index.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
alert('hi')
//# sourceMappingURL=/sm/ed2296044476ebbad3a766409a273f11d2a4aa63582d856d2768d3187e250781.map
""",
    )
