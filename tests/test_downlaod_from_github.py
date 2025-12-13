async def test_download_vb_img_from_github():
    from nonebot_plugin_fortnite.pve import download_vb_img_from_github

    vb_file = await download_vb_img_from_github()
    assert vb_file.exists()


async def test_download_shop_img_from_github():
    from nonebot_plugin_fortnite.shop import download_shop_img_from_github

    shop_file = await download_shop_img_from_github()
    assert shop_file.exists()
