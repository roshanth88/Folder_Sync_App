namespace OpenQA.Selenium.Chrome
{
    public class StableChannelChromeDriver : ChromeDriver
    {
        public StableChannelChromeDriver()
            : base(DefaultOptions)
        {
        }

        // Required for dynamic setting with `EnvironmentManager.Instance.CreateDriverInstance(options)`
        public StableChannelChromeDriver(ChromeOptions options)
            : base(options)
        {
        }

        public static ChromeOptions DefaultOptions
        {
            get { return new ChromeOptions() { AcceptInsecureCertificates = true }; }
        }
    }
}
