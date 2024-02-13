package ru.emdavl.crawler;

import edu.uci.ics.crawler4j.crawler.CrawlConfig;
import edu.uci.ics.crawler4j.crawler.CrawlController;
import edu.uci.ics.crawler4j.fetcher.PageFetcher;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtConfig;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtServer;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class WikiController {

    private static final ConcurrentHashMap<String, String> filesMap = new ConcurrentHashMap<>();

    public static void main(String[] args) throws Exception {
        String crawlStorageFolder = "/Users/e.davlyatov/IdeaProjects/mvn-sandbox/src/main/resources/root";
        int numberOfCrawlers = 7;

        CrawlConfig config = new CrawlConfig();
        config.setCrawlStorageFolder(crawlStorageFolder);
        config.setPolitenessDelay(450);
        config.setMaxPagesToFetch(120);

        // Instantiate the controller for this crawl.
        PageFetcher pageFetcher = new PageFetcher(config);
        RobotstxtConfig robotstxtConfig = new RobotstxtConfig();
        RobotstxtServer robotstxtServer = new RobotstxtServer(robotstxtConfig, pageFetcher);
        CrawlController controller = new CrawlController(config, pageFetcher, robotstxtServer);

        // For each crawl, you need to add some seed urls. These are the first
        // URLs that are fetched and then the crawler starts following links
        // which are found in these pages
        controller.addSeed("https://ru.wikipedia.org/wiki/%D0%A5%D0%BE%D1%80%D0%B4%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%B3%D1%80%D0%B0%D1%84");

        // The factory which creates instances of crawlers.
        CrawlController.WebCrawlerFactory<WikiCrawler> factory = () -> new WikiCrawler(filesMap);

        // Start the crawl. This is a blocking operation, meaning that your code
        // will reach the line after this only when crawling is finished.
        controller.start(factory, numberOfCrawlers);
        String indexPath = "/Users/e.davlyatov/IdeaProjects/mvn-sandbox/src/main/resources/crawled/index.html";
        Path file = Files.createFile(Path.of(indexPath));
        List<Map.Entry<String, String>> entries = filesMap.entrySet().stream()
                .sorted(Comparator.comparing(e -> Integer.valueOf(e.getKey().split(" ")[0])))
                .toList();
        try (var writer = new FileWriter(file.toFile())) {
            entries.forEach(elem -> {
                try {
                    writer.write("<a href=\"%s\">%s</a><br>".formatted(elem.getValue(), elem.getKey()));
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });
        }
    }


}
