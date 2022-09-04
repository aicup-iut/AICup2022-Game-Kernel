import java.util.Locale;
import java.util.Vector;
import java.util.Scanner;

public class main {
    public static void main(String[] args) {
        GameState game_state = new GameState();
        for (int i = 0; i < game_state.rounds; i++) {
            game_state.setInfo();
            System.out.println(game_state.getAction().ordinal());
        }
    }
    public static Scanner scanner = new Scanner(System.in).useLocale(Locale.US);
    
    public enum Action {
        STAY,
        MOVE_DOWN,
        MOVE_UP,
        MOVE_RIGHT,
        MOVE_LEFT,
        UPGRADE_DEFENCE,
        UPGRADE_ATTACK,
        LINEAR_ATTACK_DOWN,
        LINEAR_ATTACK_UP,
        LINEAR_ATTACK_RIGHT,
        LINEAR_ATTACK_LEFT,
        RANGED_ATTACK
    }

    public enum MapType {
        EMPTY,
        AGENT,
        GOLD,
        TREASURY,
        WALL,
        FOG,
        OUT_OF_SIGHT,
        OUT_OF_MAP
    }

    public static class Point {

        public int x;
        public int y;

        public Point(int x, int y) {
            this.x = x;
            this.y = y;
        }
    }

    public static class MapTile {
        public MapType type;
        public int data;
        public Point coordinates;
    }

    public static class Map {
        public int width, height;
        public int goldCount;
        public int sightRange;
        Vector<MapTile> grid;
    }

    public static class GameState {
        public int rounds;
        public int defUpgradeCost, atkUpgradeCost;
        public float coolDownRate;
        public int linearAttackRange, rangedAttackRadius;
        public Map map;
        public Point location;
        public int agentID;
        public int currentRound;
        public float attackRatio;
        public int deflvl, atklvl;
        public int wallet, safeWallet;
        public Vector<Integer> wallets;
        public int lastAction;

        public GameState() {
            map = new Map();
            rounds = scanner.nextInt();
            defUpgradeCost = scanner.nextInt();
            atkUpgradeCost = scanner.nextInt();
            coolDownRate = scanner.nextFloat();
            linearAttackRange = scanner.nextInt();
            rangedAttackRadius = scanner.nextInt();
            map.width = scanner.nextInt();
            map.height = scanner.nextInt();
            map.goldCount = scanner.nextInt();
            map.sightRange = scanner.nextInt(); // equivalent to (2r+1)
            map.grid = new Vector<>();
        }

        public void setInfo() {
            int x = scanner.nextInt();
            int y = scanner.nextInt();
            location = new Point(x, y); // (row, column)
            for (int i = 0; i < map.sightRange * map.sightRange; i++) {
                MapTile tile = new MapTile();
                tile.type = MapType.values()[scanner.nextInt()];
                tile.data = scanner.nextInt();
                x = scanner.nextInt();
                y = scanner.nextInt();
                tile.coordinates = new Point(x, y);
                map.grid.add(tile);
            }
            agentID = scanner.nextInt(); // player1: 0,1 --- player2: 2,3
            currentRound = scanner.nextInt(); // 1 indexed
            attackRatio = scanner.nextFloat();
            deflvl = scanner.nextInt();
            atklvl = scanner.nextInt();
            wallet = scanner.nextInt();
            safeWallet = scanner.nextInt();
            wallets = new Vector<>(); // current wallet
            for(int i = 0; i < 4; i++) {
                wallets.add(scanner.nextInt());
            }
            lastAction = scanner.nextInt(); // -1 if unsuccessful
            scanner.nextLine();
        }

        public Action getAction() {
            // write your code here
            // return the action value
            return Action.STAY;
        }
    }
}