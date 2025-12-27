async def test_download_vb_img_from_github():
    from nonebot_plugin_fortnite import pve

    vb_file = pve.get_vb_file()
    await pve.download_vb_img_from_github(vb_file)
    assert vb_file.exists()


async def test_download_shop_img_from_github():
    from nonebot_plugin_fortnite import shop

    shop_file = shop.get_shop_file()
    await shop.download_shop_img_from_github(shop_file)
    assert shop_file.exists()
