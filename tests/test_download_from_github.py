async def test_download_vb_img_from_github():
    from nonebot_plugin_fortnite import pve

    await pve.download_vb_img_from_github()
    assert pve.VB_FILE.exists()


async def test_download_shop_img_from_github():
    from nonebot_plugin_fortnite import shop

    await shop.download_shop_img_from_github()
    assert shop.SHOP_FILE.exists()
