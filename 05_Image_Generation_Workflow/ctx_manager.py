from llama_index.core.workflow import Context


async def set_image_prompt(ctx: Context, image_prompt: str) -> None:
    await ctx.store.set("image_prompt", image_prompt)


async def get_image_prompt(ctx: Context) -> str:
    image_prompt = await ctx.store.get("image_prompt", "")
    return image_prompt


async def add_query_hist(ctx: Context, user_query: str) -> None:
    query_hist = await ctx.store.get("query_hist", [])
    query_hist.append(user_query)
    await ctx.store.set("query_hist", query_hist)


async def get_query_hist(ctx: Context) -> str:
    query_hist = await ctx.store.get("query_hist", [])
    query_hist_str = "; ".join(query_hist)
    return query_hist_str


async def set_rewritten_hist(ctx: Context, rewritten_hist: str) -> None:
    await ctx.store.set("rewritten_hist", rewritten_hist)


async def get_rewritten_hist(ctx: Context) -> str:
    rewritten_prompt = await ctx.store.get("rewritten_hist", "")
    return rewritten_prompt