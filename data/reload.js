let last = null;

async function checkReload() {
  try {
    const res = await fetch("/index.html", { method: "HEAD" });

    const modified = res.headers.get("last-modified");

    if (last === null) {
      last = modified;
    } else if (modified && modified !== last) {
      console.log("FRB UI updated → reload");
      location.reload();
    }
  } catch (e) {
    console.log("reload check error");
  }
}

setInterval(checkReload, 2000);
