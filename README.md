# AirCard Fix

基于 [Mak5er/AirCard-iOS](https://github.com/Mak5er/AirCard-iOS) 的非官方修复分支，修复导入壁纸时漏传 PosterKit 隐藏配置的问题。

[下载 IPA](https://github.com/zhhshss/AirCard-iOS-depth-fix/releases/tag/v1.3.2-posterkit.1) · [安装说明](docs/INSTALL-zh.txt) · [GitHub Actions](https://github.com/zhhshss/AirCard-iOS-depth-fix/actions/workflows/build-ipa.yml) · [原项目说明与致谢](UPSTREAM-README.md)

## 修复了什么

原导入流程会跳过所有以 `.` 开头的文件，包括：

```text
.com.apple.posterkit.provider.contents.configurableOptions.plist
```

这会使壁纸包中的景深等首选渲染配置无法完整传入 PosterBoard。本分支修改 Rust 核心的两个文件传输入口，保留 `.com.apple.posterkit.*` 配置，并继续排除其他隐藏文件及 `__MACOSX`。

修复位置：[rust-core/src/exploit.rs](rust-core/src/exploit.rs)。新增回归测试直接调用实际归档函数，检查配置和图片数据保留、无关隐藏文件排除。

应用显示名称为 **AirCard Fix**，版本 `1.3.2`，构建号 `13201`，Bundle ID 保持 `com.mak5er.aircard`。

## 验证范围

- 已通过实际归档函数的回归测试、iOS arm64 编译、IPA 结构及下载哈希校验。
- 用户在 **iPad Air M3 11 英寸 / iPadOS 27.0.1** 上确认：此应用与适配后的 `ParameterizedCA` 壁纸配合，能够恢复人物遮挡时钟。
- 壁纸本身仍需要兼容的分层和配置；此修复不会自动转换旧壁纸格式或适配不同屏幕尺寸。
- 底层系统支持范围请查看[上游兼容性说明](https://github.com/Mak5er/AirCard-iOS#compatibility)。其他设备、系统和壁纸组合需要单独验证。

仓库和应用 Release 提供导入器源码及安装包，不包含测试使用的第三方壁纸素材。

## 安装与使用

1. 从 [Release](https://github.com/zhhshss/AirCard-iOS-depth-fix/releases/tag/v1.3.2-posterkit.1) 下载 IPA。IPA **未签名**，需要使用自己的签名或侧载工具安装。
2. 配置并启动 AirCard 所需的 LocalDevVPN 回环 VPN，并完成自己设备的配对；已有配置可以沿用。参考[上游配对说明](https://github.com/Mak5er/AirCard-iOS#pairing-setup-guide)。
3. 打开 **AirCard Fix → Wallpapers → Choose .tendies from Files…**，导入兼容的壁纸文件。
4. 勾选壁纸，保持 **Force PosterBoard Cache Refresh** 开启，点击 **Flash 1 Wallpaper**。
5. 等待自动刷新系统界面，再长按锁屏选用新导入的壁纸。

升级应用后需要重新导入壁纸，才能补回此前漏传的配置。

## 使用 GitHub Actions 构建

Fork 本仓库后，在 **Actions → Build AirCard wallpaper configuration fix → Run workflow** 手动启动。

流程使用 macOS runner、Xcode 16.4 和 Rust 1.99.1，依次运行回归测试、重新编译 Rust 设备库、生成 XCFramework、运行 XcodeGen、编译并校验未签名 IPA。产物在 `AirCard-PosterKit-Fix-<run number>` 中，不需要签名证书或设备配对文件作为构建机密。

**必须重新编译 Rust 核心。** 仓库保留了上游跟踪的预编译 XCFramework 和生成工程；这些旧产物不包含本次 Rust 修复。GHA 会先删除旧 XCFramework，再从修改后的源码生成新库。

## 在 Mac 上构建

准备 Xcode、XcodeGen、CMake 和 Rust 后执行：

```bash
git clone https://github.com/zhhshss/AirCard-iOS-depth-fix.git
cd AirCard-iOS-depth-fix
brew install xcodegen cmake
export DEVELOPER_DIR="$(xcode-select -p)"
rustup toolchain install 1.99.1 --profile minimal
rustup override set 1.99.1
cargo test --locked --manifest-path rust-core/Cargo.toml wallpaper_archive_tests
bash build-ios.sh
xcodegen generate
bash build-ipa.sh
```

输出：`build/AirCard-iOS.ipa`。`build-ios.sh` 会额外构建模拟器库；GHA 只构建设备库。

## 已发布构建的来源

- 上游基线：[`40640c4`](https://github.com/Mak5er/AirCard-iOS/commit/40640c4d827aeab8d798285b57d24fcf6be070d0)。
- IPA 源码提交：[`a50ddb6`](https://github.com/zhhshss/AirCard-iOS-depth-fix/commit/a50ddb67825f0c9c76786a29054ea3204ec8dd46)。
- [通过的 GHA 构建记录](https://github.com/zhhshss/AirCard-iOS-depth-fix/actions/runs/40965368047)。
- Release 随附 `build-info.json` 和 `SHA256SUMS.txt`，用于核对源码、构建工具版本及文件完整性。

## License and credits

沿用 [MIT License](LICENSE)，完整保留上游版权声明。本分支基于 Mak5er/AirCard-iOS；底层 AirLift 及其他组件的作者与致谢见 [原项目说明](UPSTREAM-README.md#credits)。

This unofficial fork preserves required `.com.apple.posterkit.*` metadata during wallpaper imports. It includes a regression test and a GitHub Actions workflow that rebuilds the Rust core before packaging an unsigned IPA. Compatible wallpaper data is still required. The tested IPA is available in Releases; upstream licensing and attribution are retained.
