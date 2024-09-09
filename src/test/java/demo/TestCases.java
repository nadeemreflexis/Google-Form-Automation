package demo;

import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeDriverService;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.logging.LogType;
import org.openqa.selenium.logging.LoggingPreferences;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import java.time.Duration;
import java.util.logging.Level;
import demo.wrappers.Wrappers;

public class TestCases {
    ChromeDriver driver;

    /*
     * TODO: Write your tests here with testng @Test annotation. 
     * Follow `testCase01` `testCase02`... format or what is provided in instructions
     */
    @Test
    public void testCase01() throws InterruptedException{
        // Navigate to google form
        driver.get("https://forms.gle/wjPkzeSEk1CM7KgGA");
        Thread.sleep(3000);
        System.out.println("wait 1");
        WebElement nameInputBox = driver.findElement(By.xpath("//input[@type='text']"));
        Wrappers.enterText(nameInputBox, "Crio Learner");
        WebElement practicingAutomationTextArea = driver.findElement(By.xpath("//textarea[contains(@class,'tL9Q4c')]"));
        String practisingAutomationText = "I want to be the best QA Engineer!";
        String epochTimeString = Wrappers.getEpochTimeAsString();
        Thread.sleep(3000);
        System.out.println("wait 2");
        Wrappers.enterText(practicingAutomationTextArea, practisingAutomationText+" "+epochTimeString);
        // select radio button as per automation experience
        Thread.sleep(3000);
        System.out.println("wait 3");
        Wrappers.radioButton(driver, "6 - 10");
        //Select checkbox for skillsets
        Thread.sleep(3000);
        System.out.println("wait 4");
        Wrappers.checkBox(driver, "Java");
        Wrappers.checkBox(driver, "Selenium");
        Wrappers.checkBox(driver, "TestNG");
        // click on dropdown
        WebElement dropDoWebElement = driver.findElement(By.xpath("//div[contains(@class,'DEh1R')]"));
        Thread.sleep(3000);
        System.out.println("wait 5");
        Wrappers.clickOnElement(driver, dropDoWebElement);
        Wrappers.dropDownClick(driver, "Mr");

        //Enter 7 days ago date
        WebElement dateInputBox = driver.findElement(By.xpath("//input[@type='date']"));
        String sevenDaysAgoDate = Wrappers.getdateSevenDaysAgo();
        Thread.sleep(3000);
        System.out.println("wait 6");
        Wrappers.enterText(dateInputBox, sevenDaysAgoDate);

        //Enter current time in HH:MM
        WebElement hourElement = driver.findElement(By.xpath("//input[@aria-label='Hour']"));
        WebElement miElement   = driver.findElement(By.xpath("//input[@aria-label='Minute']"));
        WebElement submitBtn = driver.findElement(By.xpath("//div[@class='lRwqcd']/div"));

        Wrappers.enterText(hourElement, "07");
        Wrappers.enterText(miElement, "30");
        Wrappers.clickOnElement(driver, submitBtn);

        Thread.sleep(3000);
        System.out.println("wait 7");
        WebElement successMsgElement = driver.findElement(By.xpath("//div[@class='vHW8K']"));
        String expectedSuccessMsg = "Thanks for your response, Automation Wizard!";
        Assert.assertEquals(successMsgElement.getText().trim(), expectedSuccessMsg);
    }

     
    /*
     * Do not change the provided methods unless necessary, they will help in automation and assessment
     */
    @BeforeTest
    public void startBrowser()
    {
        System.setProperty("java.util.logging.config.file", "logging.properties");

        // NOT NEEDED FOR SELENIUM MANAGER
        // WebDriverManager.chromedriver().timeout(30).setup();

        ChromeOptions options = new ChromeOptions();
        LoggingPreferences logs = new LoggingPreferences();

        logs.enable(LogType.BROWSER, Level.ALL);
        logs.enable(LogType.DRIVER, Level.ALL);
        options.setCapability("goog:loggingPrefs", logs);
        options.addArguments("--remote-allow-origins=*");

        System.setProperty(ChromeDriverService.CHROME_DRIVER_LOG_PROPERTY, "build/chromedriver.log"); 

        driver = new ChromeDriver();

        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(30));
    }

    @AfterTest
    public void endTest()
    {
        driver.close();
        driver.quit();
    }
}
